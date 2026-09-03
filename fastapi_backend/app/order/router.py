
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy import func

from app.database import get_db

from app.models import (
    Order,
    OrderItem,
    Cart,
    Product,
    User,
    Notification,
    ReturnRequest,
    Payment
)

from app.schemas import ReturnRequestCreate

from app.websocket.websocket import (
    send_order_update,
    send_notification
)

from app.dependencies import (
    get_current_user,
    require_role
)

from app.services.email_service import send_email


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


# =========================================================
# CONSTANTS
# =========================================================

RETURN_WINDOW_DAYS = 7


# =========================================================
# HELPER: SAFE USER ROLE
# =========================================================

def get_user_role(user):

    if not user:
        return ""

    return str(
        getattr(user, "role", "") or ""
    ).lower()


# =========================================================
# HELPER: SEND EMAIL SAFELY
# =========================================================

def send_order_email(
    user: User,
    order_id: int,
    subject: str,
    message: str
):

    if not user or not user.email:

        print(
            f"Email skipped for order #{order_id}: "
            "User/email not available"
        )

        return False

    try:

        send_email(
            to_email=user.email,
            subject=subject,
            body=message
        )

        print(
            f"Email sent successfully for order #{order_id}"
        )

        return True

    except Exception as e:

        print(
            f"Email failed for order #{order_id}:",
            repr(e)
        )

        return False


# =========================================================
# HELPER: CREATE DATABASE NOTIFICATION SAFELY
# =========================================================

def create_db_notification(
    db: Session,
    user_id: int,
    notification_type: str,
    message: str
):

    try:

        notification = Notification(
            user_id=user_id,
            type=notification_type,
            message=message,
            read_status=False,
            timestamp=datetime.utcnow()
        )

        db.add(notification)

        db.commit()

        db.refresh(notification)

        print(
            "Database notification created:",
            notification.id
        )

        return notification

    except Exception as e:

        db.rollback()

        print(
            "Database notification failed:",
            repr(e)
        )

        return None


# =========================================================
# HELPER: ORDER RESPONSE
# =========================================================

def order_response(order: Order):

    return {

        "id": order.id,

        "user_id": order.user_id,

        "total_amount": order.total_amount,

        "payment_status": order.payment_status,

        "order_status": order.order_status,

        "status": order.order_status,

        "created_at": order.created_at,

        "delivered_at": order.delivered_at
    }


# =========================================================
# HELPER: RETURN RESPONSE
# =========================================================

def return_response(request: ReturnRequest):

    return {

        "id": request.id,

        "order_id": request.order_id,

        "user_id": request.user_id,

        "reason": request.reason,

        "comment": request.comment,

        "status": request.status,

        "created_at": request.created_at
    }


# =========================================================
# CREATE ORDER FROM CART
# =========================================================

@router.post("/create")
async def create_order(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    user_id = current_user.id

    print()
    print("=" * 70)
    print("CREATE ORDER")
    print("User ID:", user_id)
    print("=" * 70)

    # -----------------------------------------------------
    # CHECK USER
    # -----------------------------------------------------

    user = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # -----------------------------------------------------
    # GET CART
    # -----------------------------------------------------

    cart_items = (
        db.query(Cart)
        .filter(
            Cart.user_id == user_id
        )
        .all()
    )

    if not cart_items:

        raise HTTPException(
            status_code=400,
            detail="Cart is empty"
        )

    total_amount = 0.0

    products = []

    # -----------------------------------------------------
    # CHECK PRODUCTS AND STOCK
    # -----------------------------------------------------

    for item in cart_items:

        if item.product_id is None:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Cart item {item.id} "
                    "has no product_id"
                )
            )

        if (
            item.quantity is None
            or item.quantity <= 0
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Invalid quantity for "
                    f"cart item {item.id}"
                )
            )

        # -------------------------------------------------
        # LOCK PRODUCT ROW
        # -------------------------------------------------

        product = (
            db.query(Product)
            .filter(
                Product.id == item.product_id
            )
            .with_for_update()
            .first()
        )

        if not product:

            raise HTTPException(
                status_code=404,
                detail=(
                    f"Product {item.product_id} "
                    "not found"
                )
            )

        current_stock = product.stock or 0

        if current_stock < item.quantity:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Not enough stock for "
                    f"product {product.name}. "
                    f"Available stock: {current_stock}, "
                    f"Requested: {item.quantity}"
                )
            )

        product_price = float(
            product.price or 0
        )

        total_amount += (
            product_price * item.quantity
        )

        products.append(
            (
                item,
                product,
                product_price
            )
        )

    # -----------------------------------------------------
    # VALIDATE TOTAL
    # -----------------------------------------------------

    if total_amount <= 0:

        raise HTTPException(
            status_code=400,
            detail="Invalid order total."
        )

    # -----------------------------------------------------
    # CREATE ORDER
    # -----------------------------------------------------

    try:

        order = Order(
            user_id=user_id,
            total_amount=total_amount,
            payment_status="Pending",
            order_status="Pending"
        )

        db.add(order)

        # -------------------------------------------------
        # FLUSH
        # -------------------------------------------------

        db.flush()

        print(
            f"Order created in transaction: #{order.id}"
        )

        # -------------------------------------------------
        # CREATE ORDER ITEMS
        # -------------------------------------------------

        for (
            item,
            product,
            product_price
        ) in products:

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item.quantity,
                price=product_price
            )

            db.add(order_item)

        # -------------------------------------------------
        # REDUCE STOCK
        # -------------------------------------------------

        for (
            item,
            product,
            product_price
        ) in products:

            product.stock = (
                (product.stock or 0)
                - item.quantity
            )

        # -------------------------------------------------
        # CLEAR CART
        # -------------------------------------------------

        for (
            item,
            product,
            product_price
        ) in products:

            db.delete(item)

        # -------------------------------------------------
        # SINGLE COMMIT
        # -------------------------------------------------

        db.commit()

        db.refresh(order)

    except HTTPException:

        db.rollback()
        raise

    except Exception as e:

        db.rollback()

        print(
            "Order creation failed:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to create order."
        )

    print(
        f"ORDER CREATED: {order.id}"
    )

    # -----------------------------------------------------
    # DATABASE NOTIFICATION
    # -----------------------------------------------------

    notification_message = (
        f"Your order #{order.id} "
        "has been created successfully."
    )

    notification = create_db_notification(
        db=db,
        user_id=user_id,
        notification_type="order",
        message=notification_message
    )

    # -----------------------------------------------------
    # WEBSOCKET ORDER UPDATE
    # -----------------------------------------------------

    websocket_sent = False

    try:

        websocket_sent = await send_order_update(
            user_id=user_id,
            order_id=order.id,
            status=order.order_status
        )

    except Exception as e:

        print(
            "Create order WebSocket failed:",
            repr(e)
        )

    # -----------------------------------------------------
    # WEBSOCKET NOTIFICATION
    # -----------------------------------------------------

    notification_websocket_sent = False

    if notification:

        try:

            notification_websocket_sent = (
                await send_notification(
                    user_id=user_id,
                    notification_type="order",
                    message=notification_message,
                    notification_id=notification.id
                )
            )

        except Exception as e:

            print(
                "Create order notification WebSocket failed:",
                repr(e)
            )

    # -----------------------------------------------------
    # EMAIL
    # -----------------------------------------------------

    email_sent = send_order_email(
        user=user,
        order_id=order.id,
        subject=(
            f"Smart Ecommerce - "
            f"Order #{order.id} Created"
        ),
        message=notification_message
    )

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return {

        "message":
            "Order created successfully",

        "order":
            order_response(order),

        "email_sent":
            email_sent,

        "websocket_sent":
            websocket_sent,

        "notification_websocket_sent":
            notification_websocket_sent
    }


# =========================================================
# GET USER ORDERS
# =========================================================

@router.get("/")
def get_orders(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    orders = (
        db.query(Order)
        .filter(
            Order.user_id == current_user.id
        )
        .order_by(
            Order.id.desc()
        )
        .all()
    )

    return [
        order_response(order)
        for order in orders
    ]


# =========================================================
# PAYMENT SUCCESS
# =========================================================
#
# This endpoint creates/updates the Payment row.
#
# IMPORTANT:
#
# For REAL Stripe Checkout payments, the Stripe webhook
# remains the source of truth for the Stripe transaction ID.
#
# This endpoint is useful for manual/COD payment completion.
#
# =========================================================

@router.put("/{order_id}/pay")
async def payment_success(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    print()
    print("=" * 70)
    print("PAYMENT SUCCESS / MANUAL PAYMENT")
    print("Order ID:", order_id)
    print("=" * 70)

    # -----------------------------------------------------
    # FIND ORDER
    # -----------------------------------------------------

    order = (
        db.query(Order)
        .filter(
            Order.id == order_id
        )
        .first()
    )

    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order Not Found"
        )

    # -----------------------------------------------------
    # AUTHORIZATION
    # -----------------------------------------------------

    if (
        get_user_role(current_user) != "admin"
        and order.user_id != current_user.id
    ):

        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )

    # -----------------------------------------------------
    # FIND EXISTING PAYMENT
    # -----------------------------------------------------

    payment = (
        db.query(Payment)
        .filter(
            Payment.order_id == order.id
        )
        .order_by(
            Payment.id.desc()
        )
        .first()
    )

    # -----------------------------------------------------
    # IF EXISTING PAYMENT IS STRIPE
    # -----------------------------------------------------

    if payment:

        payment_method = (
            str(
                payment.payment_method or ""
            )
            .lower()
            .strip()
        )

        if payment_method == "stripe":

            raise HTTPException(
                status_code=400,
                detail=(
                    "Stripe payments must be confirmed "
                    "by the Stripe webhook. "
                    "Do not call this endpoint for "
                    "Stripe payments."
                )
            )

    # -----------------------------------------------------
    # ALREADY PAID
    # -----------------------------------------------------

    if str(
        order.payment_status or ""
    ).lower() == "paid":

        # -------------------------------------------------
        # IMPORTANT FIX
        #
        # Even if the Order says Paid, make sure the
        # Payment row exists.
        # -------------------------------------------------

        if payment is None:

            print(
                "Order is already Paid but Payment "
                "record is missing."
            )

            print(
                "Creating missing Payment record..."
            )

            payment = Payment(
                order_id=order.id,
                amount=order.total_amount,
                payment_method="manual",
                transaction_id=None,
                status="Paid"
            )

            db.add(payment)

            try:

                db.commit()

                db.refresh(order)
                db.refresh(payment)

                print(
                    "MISSING PAYMENT CREATED:",
                    payment.id
                )

            except Exception as e:

                db.rollback()

                print(
                    "Failed to create missing Payment:",
                    repr(e)
                )

                raise HTTPException(
                    status_code=500,
                    detail=(
                        "Order is already paid, "
                        "but payment record could not "
                        "be created."
                    )
                )

        return {

            "message":
                "Order already paid",

            "order":
                order_response(order),

            "payment": {

                "id":
                    payment.id,

                "amount":
                    payment.amount,

                "payment_method":
                    payment.payment_method,

                "status":
                    payment.status,

                "transaction_id":
                    payment.transaction_id
            },

            "email_sent":
                False,

            "websocket_sent":
                False,

            "notification_websocket_sent":
                False
        }

    # -----------------------------------------------------
    # CREATE PAYMENT IF MISSING
    # -----------------------------------------------------

    if payment is None:

        print(
            "No Payment record found."
        )

        print(
            "Creating Payment record for order:",
            order.id
        )

        payment = Payment(

            order_id=order.id,

            amount=order.total_amount,

            payment_method="manual",

            transaction_id=None,

            status="Paid"
        )

        db.add(payment)

        # -------------------------------------------------
        # FLUSH TO GET PAYMENT ID
        # -------------------------------------------------

        db.flush()

        print(
            "NEW PAYMENT CREATED:",
            payment.id
        )

    else:

        print(
            "Existing Payment found:",
            payment.id
        )

        payment.amount = order.total_amount

        payment.payment_method = "manual"

        payment.status = "Paid"

    # -----------------------------------------------------
    # UPDATE ORDER
    # -----------------------------------------------------

    order.payment_status = "Paid"

    order.order_status = "Confirmed"

    # -----------------------------------------------------
    # COMMIT PAYMENT + ORDER TOGETHER
    # -----------------------------------------------------

    try:

        db.commit()

        db.refresh(order)

        db.refresh(payment)

        print(
            "PAYMENT DATABASE UPDATED"
        )

        print(
            "Payment ID:",
            payment.id
        )

        print(
            "Payment Amount:",
            payment.amount
        )

        print(
            "Payment Method:",
            payment.payment_method
        )

        print(
            "Payment Status:",
            payment.status
        )

        print(
            "Order Payment Status:",
            order.payment_status
        )

        print(
            "Order Status:",
            order.order_status
        )

    except Exception as e:

        db.rollback()

        print(
            "Manual payment update failed:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to update payment status."
        )

    # -----------------------------------------------------
    # GET USER
    # -----------------------------------------------------

    user = (
        db.query(User)
        .filter(
            User.id == order.user_id
        )
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # -----------------------------------------------------
    # DATABASE NOTIFICATION
    # -----------------------------------------------------

    notification_message = (
        f"Payment successful for "
        f"order #{order.id}."
    )

    notification = create_db_notification(
        db=db,
        user_id=order.user_id,
        notification_type="payment",
        message=notification_message
    )

    # -----------------------------------------------------
    # WEBSOCKET ORDER UPDATE
    # -----------------------------------------------------

    websocket_sent = False

    try:

        websocket_sent = await send_order_update(
            user_id=order.user_id,
            order_id=order.id,
            status=order.order_status
        )

    except Exception as e:

        print(
            "Payment order WebSocket failed:",
            repr(e)
        )

    # -----------------------------------------------------
    # WEBSOCKET NOTIFICATION
    # -----------------------------------------------------

    notification_websocket_sent = False

    if notification:

        try:

            notification_websocket_sent = (
                await send_notification(
                    user_id=order.user_id,
                    notification_type="payment",
                    message=notification_message,
                    notification_id=notification.id
                )
            )

        except Exception as e:

            print(
                "Payment notification WebSocket failed:",
                repr(e)
            )

    # -----------------------------------------------------
    # EMAIL
    # -----------------------------------------------------

    email_sent = send_order_email(
        user=user,
        order_id=order.id,
        subject=(
            f"Smart Ecommerce - "
            f"Payment Successful #{order.id}"
        ),
        message=notification_message
    )

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return {

        "message":
            "Payment successful",

        "order":
            order_response(order),

        "payment": {

            "id":
                payment.id,

            "amount":
                payment.amount,

            "payment_method":
                payment.payment_method,

            "status":
                payment.status,

            "transaction_id":
                payment.transaction_id
        },

        "email_sent":
            email_sent,

        "websocket_sent":
            websocket_sent,

        "notification_websocket_sent":
            notification_websocket_sent
    }


# =========================================================
# UPDATE ORDER STATUS
# =========================================================

@router.put("/{order_id}/status")
async def update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):

    print()
    print("=" * 70)
    print("UPDATE ORDER STATUS")
    print(
        f"Order={order_id}, "
        f"New Status={status}"
    )
    print("=" * 70)

    # -----------------------------------------------------
    # FIND ORDER
    # -----------------------------------------------------

    order = (
        db.query(Order)
        .filter(
            Order.id == order_id
        )
        .first()
    )

    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order Not Found"
        )

    # -----------------------------------------------------
    # VALID STATUSES
    # -----------------------------------------------------

    valid_statuses = [

        "Pending",
        "Confirmed",
        "Processing",
        "Shipped",
        "Delivered",
        "Cancelled",
        "Return Requested",
        "Returned"
    ]

    if status not in valid_statuses:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid status. "
                "Use: Pending, Confirmed, Processing, "
                "Shipped, Delivered, Cancelled, "
                "Return Requested, or Returned"
            )
        )

    # -----------------------------------------------------
    # PREVENT MANUAL STATUS CHANGE AFTER RETURN
    # -----------------------------------------------------

    if order.order_status == "Returned":

        if status != "Returned":

            raise HTTPException(
                status_code=400,
                detail=(
                    "A returned order must remain "
                    "in Returned status."
                )
            )

    # -----------------------------------------------------
    # UPDATE STATUS
    # -----------------------------------------------------

    order.order_status = status

    # -----------------------------------------------------
    # SET DELIVERED DATE
    # -----------------------------------------------------

    if status == "Delivered":

        if not order.delivered_at:

            order.delivered_at = datetime.utcnow()

    # -----------------------------------------------------
    # COMMIT
    # -----------------------------------------------------

    try:

        db.commit()

        db.refresh(order)

    except Exception as e:

        db.rollback()

        print(
            "Order status update failed:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to update order status."
        )

    # -----------------------------------------------------
    # GET USER
    # -----------------------------------------------------

    user = (
        db.query(User)
        .filter(
            User.id == order.user_id
        )
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # -----------------------------------------------------
    # DATABASE NOTIFICATION
    # -----------------------------------------------------

    notification_message = (
        f"Your order #{order.id} "
        f"is now {status}."
    )

    notification = create_db_notification(
        db=db,
        user_id=order.user_id,
        notification_type="order",
        message=notification_message
    )

    # -----------------------------------------------------
    # WEBSOCKET ORDER UPDATE
    # -----------------------------------------------------

    websocket_sent = False

    try:

        websocket_sent = await send_order_update(
            user_id=order.user_id,
            order_id=order.id,
            status=order.order_status
        )

    except Exception as e:

        print(
            "Status WebSocket failed:",
            repr(e)
        )

    # -----------------------------------------------------
    # WEBSOCKET NOTIFICATION
    # -----------------------------------------------------

    notification_websocket_sent = False

    if notification:

        try:

            notification_websocket_sent = (
                await send_notification(
                    user_id=order.user_id,
                    notification_type="order",
                    message=notification_message,
                    notification_id=notification.id
                )
            )

        except Exception as e:

            print(
                "Status notification WebSocket failed:",
                repr(e)
            )

    # -----------------------------------------------------
    # EMAIL MESSAGE
    # -----------------------------------------------------

    email_message = notification_message

    if status == "Shipped":

        email_message = (
            f"Your order #{order.id} "
            "has been shipped."
        )

    elif status == "Delivered":

        email_message = (
            f"Your order #{order.id} "
            "has been delivered."
        )

    elif status == "Cancelled":

        email_message = (
            f"Your order #{order.id} "
            "has been cancelled."
        )

    elif status == "Confirmed":

        email_message = (
            f"Your order #{order.id} "
            "has been confirmed."
        )

    elif status == "Processing":

        email_message = (
            f"Your order #{order.id} "
            "is being processed."
        )

    elif status == "Return Requested":

        email_message = (
            f"Return requested for "
            f"order #{order.id}."
        )

    elif status == "Returned":

        email_message = (
            f"Your order #{order.id} "
            "has been returned."
        )

    elif status == "Pending":

        email_message = (
            f"Your order #{order.id} "
            "is now pending."
        )

    # -----------------------------------------------------
    # EMAIL
    # -----------------------------------------------------

    email_sent = send_order_email(
        user=user,
        order_id=order.id,
        subject=(
            f"Smart Ecommerce - "
            f"Order #{order.id} {status}"
        ),
        message=email_message
    )

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return {

        "message":
            "Order status updated successfully",

        "order":
            order_response(order),

        "email_sent":
            email_sent,

        "websocket_sent":
            websocket_sent,

        "notification_websocket_sent":
            notification_websocket_sent
    }


# =========================================================
# TOP-SELLING PRODUCTS
# =========================================================

@router.get("/analytics/top-selling")
def top_selling_products(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):

    results = (
        db.query(
            Product.id,
            Product.name,
            func.sum(
                OrderItem.quantity
            ).label("total_quantity")
        )
        .join(
            OrderItem,
            OrderItem.product_id == Product.id
        )
        .join(
            Order,
            Order.id == OrderItem.order_id
        )
        .filter(
            Order.payment_status.ilike("Paid")
        )
        .group_by(
            Product.id,
            Product.name
        )
        .order_by(
            func.sum(
                OrderItem.quantity
            ).desc()
        )
        .limit(10)
        .all()
    )

    return [

        {

            "product_id":
                product_id,

            "product_name":
                product_name,

            "quantity_sold":
                int(total_quantity or 0)
        }

        for (
            product_id,
            product_name,
            total_quantity
        ) in results
    ]


# =========================================================
# GET ALL RETURN REQUESTS
# =========================================================

@router.get("/returns")
def get_all_return_requests(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):

    print()
    print("=" * 70)
    print("GET ALL RETURN REQUESTS")
    print("=" * 70)

    requests = (
        db.query(ReturnRequest)
        .order_by(
            ReturnRequest.id.desc()
        )
        .all()
    )

    result = [
        return_response(request)
        for request in requests
    ]

    print(
        "Return requests found:",
        len(result)
    )

    return result


# =========================================================
# GET SINGLE RETURN REQUEST
# =========================================================

@router.get("/returns/{return_id}")
def get_return_request(
    return_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    request = (
        db.query(ReturnRequest)
        .filter(
            ReturnRequest.id == return_id
        )
        .first()
    )

    if not request:

        raise HTTPException(
            status_code=404,
            detail="Return request not found"
        )

    # -----------------------------------------------------
    # AUTHORIZATION
    # -----------------------------------------------------

    if (
        get_user_role(current_user) != "admin"
        and request.user_id != current_user.id
    ):

        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )

    return return_response(request)


# =========================================================
# REQUEST RETURN
# =========================================================

@router.post("/{order_id}/return")
async def request_return(
    order_id: int,
    data: ReturnRequestCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    print()
    print("=" * 70)
    print("REQUEST RETURN")
    print("Order ID:", order_id)
    print("User ID:", current_user.id)
    print("=" * 70)

    # -----------------------------------------------------
    # FIND ORDER
    # -----------------------------------------------------

    order = (
        db.query(Order)
        .filter(
            Order.id == order_id
        )
        .first()
    )

    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # -----------------------------------------------------
    # CUSTOMER CAN RETURN ONLY OWN ORDER
    # -----------------------------------------------------

    if (
        get_user_role(current_user) != "admin"
        and order.user_id != current_user.id
    ):

        raise HTTPException(
            status_code=403,
            detail="Not authorized to return this order"
        )

    # -----------------------------------------------------
    # ONLY DELIVERED ORDERS
    # -----------------------------------------------------

    if order.order_status != "Delivered":

        raise HTTPException(
            status_code=400,
            detail=(
                "Only delivered orders "
                "can be returned"
            )
        )

    # -----------------------------------------------------
    # PAYMENT MUST BE PAID
    # -----------------------------------------------------

    if str(
        order.payment_status or ""
    ).lower() != "paid":

        raise HTTPException(
            status_code=400,
            detail=(
                "Only paid orders can be returned."
            )
        )

    # -----------------------------------------------------
    # CHECK DELIVERED DATE
    # -----------------------------------------------------

    if not order.delivered_at:

        raise HTTPException(
            status_code=400,
            detail=(
                "Delivery date is missing. "
                "Return cannot be processed."
            )
        )

    # -----------------------------------------------------
    # RETURN WINDOW
    # -----------------------------------------------------

    current_time = datetime.utcnow()

    return_deadline = (
        order.delivered_at
        + timedelta(
            days=RETURN_WINDOW_DAYS
        )
    )

    if current_time > return_deadline:

        raise HTTPException(
            status_code=400,
            detail=(
                "Return window expired. "
                "Returns are allowed within "
                "7 days after delivery."
            )
        )

    # -----------------------------------------------------
    # CHECK EXISTING REQUEST
    # -----------------------------------------------------

    existing_request = (
        db.query(ReturnRequest)
        .filter(
            ReturnRequest.order_id == order.id
        )
        .first()
    )

    if existing_request:

        raise HTTPException(
            status_code=400,
            detail=(
                "Return request already exists "
                f"with status: "
                f"{existing_request.status}"
            )
        )

    # -----------------------------------------------------
    # CREATE RETURN REQUEST
    # -----------------------------------------------------

    try:

        return_request = ReturnRequest(

            order_id=order.id,

            user_id=order.user_id,

            reason=data.reason,

            comment=data.comment,

            status="pending"
        )

        db.add(return_request)

        # -------------------------------------------------
        # UPDATE ORDER
        # -------------------------------------------------

        order.order_status = "Return Requested"

        db.commit()

        db.refresh(return_request)
        db.refresh(order)

    except Exception as e:

        db.rollback()

        print(
            "Return request creation failed:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to create return request."
        )

    # -----------------------------------------------------
    # DATABASE NOTIFICATION
    # -----------------------------------------------------

    notification_message = (
        f"Your return request for "
        f"order #{order.id} "
        "has been submitted successfully."
    )

    notification = create_db_notification(
        db=db,
        user_id=order.user_id,
        notification_type="return",
        message=notification_message
    )

    # -----------------------------------------------------
    # GET USER
    # -----------------------------------------------------

    user = (
        db.query(User)
        .filter(
            User.id == order.user_id
        )
        .first()
    )

    # -----------------------------------------------------
    # WEBSOCKET ORDER UPDATE
    # -----------------------------------------------------

    websocket_sent = False

    try:

        websocket_sent = await send_order_update(
            user_id=order.user_id,
            order_id=order.id,
            status=order.order_status
        )

    except Exception as e:

        print(
            "Return order WebSocket failed:",
            repr(e)
        )

    # -----------------------------------------------------
    # WEBSOCKET NOTIFICATION
    # -----------------------------------------------------

    notification_websocket_sent = False

    if notification:

        try:

            notification_websocket_sent = (
                await send_notification(
                    user_id=order.user_id,
                    notification_type="return",
                    message=notification_message,
                    notification_id=notification.id
                )
            )

        except Exception as e:

            print(
                "Return notification WebSocket failed:",
                repr(e)
            )

    # -----------------------------------------------------
    # EMAIL
    # -----------------------------------------------------

    email_sent = send_order_email(
        user=user,
        order_id=order.id,
        subject=(
            f"Smart Ecommerce - "
            f"Return Request #{order.id}"
        ),
        message=notification_message
    )

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return {

        "message":
            "Return request submitted successfully",

        "return_request":
            return_response(return_request),

        "order_status":
            order.order_status,

        "email_sent":
            email_sent,

        "websocket_sent":
            websocket_sent,

        "notification_websocket_sent":
            notification_websocket_sent
    }


# =========================================================
# LEGACY APPROVE RETURN
# =========================================================

@router.put("/returns/{return_id}/approve")
async def approve_return(
    return_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):

    print()
    print("=" * 70)
    print("LEGACY APPROVE RETURN")
    print("Return Request ID:", return_id)
    print("=" * 70)

    request = (
        db.query(ReturnRequest)
        .filter(
            ReturnRequest.id == return_id
        )
        .with_for_update()
        .first()
    )

    if not request:

        raise HTTPException(
            status_code=404,
            detail="Return request not found"
        )

    if str(
        request.status or ""
    ).lower() != "pending":

        raise HTTPException(
            status_code=400,
            detail=(
                f"Return request is already "
                f"{request.status}"
            )
        )

    order = (
        db.query(Order)
        .filter(
            Order.id == request.order_id
        )
        .with_for_update()
        .first()
    )

    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order.order_status != "Return Requested":

        raise HTTPException(
            status_code=400,
            detail=(
                "Return can only be approved when "
                "order status is Return Requested."
            )
        )

    # -----------------------------------------------------
    # APPROVE
    # -----------------------------------------------------

    request.status = "approved"

    order.order_status = "Returned"

    try:

        db.commit()

        db.refresh(request)
        db.refresh(order)

    except Exception as e:

        db.rollback()

        print(
            "Legacy return approval failed:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to approve return."
        )

    # -----------------------------------------------------
    # NOTIFICATION
    # -----------------------------------------------------

    notification_message = (
        f"Your return request for "
        f"order #{order.id} "
        "has been approved."
    )

    notification = create_db_notification(
        db=db,
        user_id=request.user_id,
        notification_type="return",
        message=notification_message
    )

    # -----------------------------------------------------
    # USER
    # -----------------------------------------------------

    user = (
        db.query(User)
        .filter(
            User.id == request.user_id
        )
        .first()
    )

    # -----------------------------------------------------
    # WEBSOCKET
    # -----------------------------------------------------

    websocket_sent = False

    try:

        websocket_sent = await send_order_update(
            user_id=request.user_id,
            order_id=order.id,
            status=order.order_status
        )

    except Exception as e:

        print(
            "Approve WebSocket failed:",
            repr(e)
        )

    notification_websocket_sent = False

    if notification:

        try:

            notification_websocket_sent = (
                await send_notification(
                    user_id=request.user_id,
                    notification_type="return",
                    message=notification_message,
                    notification_id=notification.id
                )
            )

        except Exception as e:

            print(
                "Approve notification WebSocket failed:",
                repr(e)
            )

    # -----------------------------------------------------
    # EMAIL
    # -----------------------------------------------------

    email_sent = send_order_email(
        user=user,
        order_id=order.id,
        subject=(
            f"Smart Ecommerce - "
            f"Return Approved #{order.id}"
        ),
        message=notification_message
    )

    return {

        "message":
            "Return approved successfully",

        "return_request_id":
            request.id,

        "status":
            request.status,

        "order_status":
            order.order_status,

        "email_sent":
            email_sent,

        "websocket_sent":
            websocket_sent,

        "notification_websocket_sent":
            notification_websocket_sent,

        "note":
            "Use POST /admin/returns/{return_id}/approve "
            "for the complete admin return workflow including inventory restoration."
    }


# =========================================================
# LEGACY REJECT RETURN
# =========================================================

@router.put("/returns/{return_id}/reject")
async def reject_return(
    return_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):

    print()
    print("=" * 70)
    print("REJECT RETURN")
    print("Return Request ID:", return_id)
    print("=" * 70)

    request = (
        db.query(ReturnRequest)
        .filter(
            ReturnRequest.id == return_id
        )
        .with_for_update()
        .first()
    )

    if not request:

        raise HTTPException(
            status_code=404,
            detail="Return request not found"
        )

    if str(
        request.status or ""
    ).lower() != "pending":

        raise HTTPException(
            status_code=400,
            detail=(
                f"Return request is already "
                f"{request.status}"
            )
        )

    order = (
        db.query(Order)
        .filter(
            Order.id == request.order_id
        )
        .with_for_update()
        .first()
    )

    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order.order_status != "Return Requested":

        raise HTTPException(
            status_code=400,
            detail=(
                "Return can only be rejected when "
                "order status is Return Requested."
            )
        )

    # -----------------------------------------------------
    # REJECT
    # -----------------------------------------------------

    request.status = "rejected"

    order.order_status = "Delivered"

    try:

        db.commit()

        db.refresh(request)
        db.refresh(order)

    except Exception as e:

        db.rollback()

        print(
            "Return rejection failed:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to reject return."
        )

    # -----------------------------------------------------
    # NOTIFICATION
    # -----------------------------------------------------

    notification_message = (
        f"Your return request for "
        f"order #{order.id} "
        "has been rejected."
    )

    notification = create_db_notification(
        db=db,
        user_id=request.user_id,
        notification_type="return",
        message=notification_message
    )

    # -----------------------------------------------------
    # USER
    # -----------------------------------------------------

    user = (
        db.query(User)
        .filter(
            User.id == request.user_id
        )
        .first()
    )

    # -----------------------------------------------------
    # WEBSOCKET
    # -----------------------------------------------------

    websocket_sent = False

    try:

        websocket_sent = await send_order_update(
            user_id=request.user_id,
            order_id=order.id,
            status=order.order_status
        )

    except Exception as e:

        print(
            "Reject WebSocket failed:",
            repr(e)
        )

    notification_websocket_sent = False

    if notification:

        try:

            notification_websocket_sent = (
                await send_notification(
                    user_id=request.user_id,
                    notification_type="return",
                    message=notification_message,
                    notification_id=notification.id
                )
            )

        except Exception as e:

            print(
                "Reject notification WebSocket failed:",
                repr(e)
            )

    # -----------------------------------------------------
    # EMAIL
    # -----------------------------------------------------

    email_sent = send_order_email(
        user=user,
        order_id=order.id,
        subject=(
            f"Smart Ecommerce - "
            f"Return Rejected #{order.id}"
        ),
        message=notification_message
    )

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return {

        "message":
            "Return rejected successfully",

        "return_request_id":
            request.id,

        "status":
            request.status,

        "order_status":
            order.order_status,

        "email_sent":
            email_sent,

        "websocket_sent":
            websocket_sent,

        "notification_websocket_sent":
            notification_websocket_sent
    }


# =========================================================
# GET SINGLE ORDER
# =========================================================

@router.get("/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # -----------------------------------------------------
    # FIND ORDER
    # -----------------------------------------------------

    order = (
        db.query(Order)
        .filter(
            Order.id == order_id
        )
        .first()
    )

    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order Not Found"
        )

    # -----------------------------------------------------
    # AUTHORIZATION
    # -----------------------------------------------------

    if (
        get_user_role(current_user) != "admin"
        and order.user_id != current_user.id
    ):

        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )

    return order_response(order)

