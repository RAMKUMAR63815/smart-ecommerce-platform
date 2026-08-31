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
    ReturnRequest
)

from app.schemas import ReturnRequestCreate

from app.websocket.websocket import (
    send_order_update,
    send_notification
)

from app.services.email_service import send_email


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


# =========================================================
# CONSTANTS
# =========================================================

RETURN_WINDOW_DAYS = 7


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

        return True

    except Exception as e:

        print(
            f"Email failed for order #{order_id}:",
            e
        )

        return False


# =========================================================
# HELPER: CREATE DATABASE NOTIFICATION
# =========================================================

def create_db_notification(
    db: Session,
    user_id: int,
    notification_type: str,
    message: str
):

    notification = Notification(
        user_id=user_id,
        type=notification_type,
        message=message,
        read_status=False
    )

    db.add(notification)

    db.commit()

    db.refresh(notification)

    return notification


# =========================================================
# CREATE ORDER FROM CART
# =========================================================

@router.post("/create")
async def create_order(
    user_id: int,
    db: Session = Depends(get_db)
):

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
        .filter(User.id == user_id)
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
        .filter(Cart.user_id == user_id)
        .all()
    )

    if not cart_items:

        raise HTTPException(
            status_code=400,
            detail="Cart is empty"
        )

    total_amount = 0

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

        product = (
            db.query(Product)
            .filter(Product.id == item.product_id)
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

        if product.stock < item.quantity:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Not enough stock for "
                    f"product {product.name}. "
                    f"Available stock: {product.stock}, "
                    f"Requested: {item.quantity}"
                )
            )

        total_amount += (
            product.price * item.quantity
        )

        products.append(
            (item, product)
        )

    # -----------------------------------------------------
    # CREATE ORDER
    # -----------------------------------------------------

    order = Order(
        user_id=user_id,
        total_amount=total_amount,
        payment_status="Pending",
        order_status="Pending"
    )

    db.add(order)

    db.commit()

    db.refresh(order)

    print(
        f"Order created: #{order.id}"
    )

    # -----------------------------------------------------
    # CREATE ORDER ITEMS
    # -----------------------------------------------------

    for item, product in products:

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item.quantity,
            price=product.price
        )

        db.add(order_item)

    db.commit()

    # -----------------------------------------------------
    # REDUCE STOCK
    # -----------------------------------------------------

    for item, product in products:

        product.stock -= item.quantity

    # -----------------------------------------------------
    # CLEAR CART
    # -----------------------------------------------------

    for item, product in products:

        db.delete(item)

    db.commit()

    db.refresh(order)

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
            e
        )

    # -----------------------------------------------------
    # WEBSOCKET NOTIFICATION
    # -----------------------------------------------------

    notification_websocket_sent = False

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
            e
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

        "order": {

            "id":
                order.id,

            "user_id":
                order.user_id,

            "total_amount":
                order.total_amount,

            "payment_status":
                order.payment_status,

            "order_status":
                order.order_status,

            "status":
                order.order_status,

            "created_at":
                order.created_at
        },

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
    user_id: int,
    db: Session = Depends(get_db)
):

    orders = (
        db.query(Order)
        .filter(
            Order.user_id == user_id
        )
        .order_by(
            Order.id.desc()
        )
        .all()
    )

    result = []

    for order in orders:

        result.append({

            "id":
                order.id,

            "user_id":
                order.user_id,

            "total_amount":
                order.total_amount,

            "payment_status":
                order.payment_status,

            "order_status":
                order.order_status,

            "status":
                order.order_status,

            "created_at":
                order.created_at
        })

    return result


# =========================================================
# PAYMENT SUCCESS
# =========================================================

@router.put("/{order_id}/pay")
async def payment_success(
    order_id: int,
    db: Session = Depends(get_db)
):

    print()
    print("=" * 70)
    print("PAYMENT SUCCESS")
    print("Order ID:", order_id)
    print("=" * 70)

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

    if order.payment_status == "Paid":

        return {

            "message":
                "Order already paid",

            "order": {

                "id":
                    order.id,

                "user_id":
                    order.user_id,

                "total_amount":
                    order.total_amount,

                "payment_status":
                    order.payment_status,

                "order_status":
                    order.order_status,

                "status":
                    order.order_status,

                "created_at":
                    order.created_at
            },

            "email_sent":
                False,

            "websocket_sent":
                False,

            "notification_websocket_sent":
                False
        }

    order.payment_status = "Paid"

    order.order_status = "Confirmed"

    db.commit()

    db.refresh(order)

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
            e
        )

    notification_websocket_sent = False

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
            e
        )

    email_sent = send_order_email(
        user=user,
        order_id=order.id,
        subject=(
            f"Smart Ecommerce - "
            f"Payment Successful #{order.id}"
        ),
        message=notification_message
    )

    return {

        "message":
            "Payment successful",

        "order": {

            "id":
                order.id,

            "user_id":
                order.user_id,

            "total_amount":
                order.total_amount,

            "payment_status":
                order.payment_status,

            "order_status":
                order.order_status,

            "status":
                order.order_status,

            "created_at":
                order.created_at
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
    db: Session = Depends(get_db)
):

    print()
    print("=" * 70)
    print("UPDATE ORDER STATUS")
    print(
        f"Order={order_id}, "
        f"New Status={status}"
    )
    print("=" * 70)

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

    order.order_status = status

    db.commit()

    db.refresh(order)

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
            e
        )

    notification_websocket_sent = False

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
            e
        )

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

    email_sent = send_order_email(
        user=user,
        order_id=order.id,
        subject=(
            f"Smart Ecommerce - "
            f"Order #{order.id} {status}"
        ),
        message=email_message
    )

    return {

        "message":
            "Order status updated successfully",

        "order": {

            "id":
                order.id,

            "user_id":
                order.user_id,

            "total_amount":
                order.total_amount,

            "payment_status":
                order.payment_status,

            "order_status":
                order.order_status,

            "status":
                order.order_status,

            "created_at":
                order.created_at
        },

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
#
# IMPORTANT:
# This static route MUST be before /{order_id}
#
# GET /orders/analytics/top-selling
# =========================================================

@router.get("/analytics/top-selling")
def top_selling_products(
    db: Session = Depends(get_db)
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
#
# IMPORTANT:
# This MUST appear before /{order_id}
#
# GET /orders/returns
# =========================================================

@router.get("/returns")
def get_all_return_requests(
    db: Session = Depends(get_db)
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

    result = []

    for request in requests:

        result.append({

            "id":
                request.id,

            "order_id":
                request.order_id,

            "user_id":
                request.user_id,

            "reason":
                request.reason,

            "comment":
                request.comment,

            "status":
                request.status,

            "created_at":
                request.created_at
        })

    print(
        "Return requests found:",
        len(result)
    )

    return result


# =========================================================
# GET SINGLE RETURN REQUEST
# =========================================================
#
# GET /orders/returns/{return_id}
# =========================================================

@router.get("/returns/{return_id}")
def get_return_request(
    return_id: int,
    db: Session = Depends(get_db)
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

    return {

        "id":
            request.id,

        "order_id":
            request.order_id,

        "user_id":
            request.user_id,

        "reason":
            request.reason,

        "comment":
            request.comment,

        "status":
            request.status,

        "created_at":
            request.created_at
    }


# =========================================================
# REQUEST RETURN
# =========================================================
#
# POST /orders/{order_id}/return
#
# Body:
#
# {
#     "reason": "Product damaged",
#     "comment": "Product was damaged."
# }
#
# =========================================================

@router.post("/{order_id}/return")
async def request_return(
    order_id: int,
    data: ReturnRequestCreate,
    db: Session = Depends(get_db)
):

    print()
    print("=" * 70)
    print("REQUEST RETURN")
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
            detail="Order not found"
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
    # RETURN WINDOW
    # -----------------------------------------------------

    if not order.created_at:

        raise HTTPException(
            status_code=400,
            detail="Order creation date is missing"
        )

    current_time = datetime.utcnow()

    return_deadline = (
        order.created_at
        + timedelta(days=RETURN_WINDOW_DAYS)
    )

    if current_time > return_deadline:

        raise HTTPException(
            status_code=400,
            detail=(
                "Return window expired. "
                "Returns are allowed within "
                "7 days."
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

    return_request = ReturnRequest(

        order_id=order.id,

        user_id=order.user_id,

        reason=data.reason,

        comment=data.comment,

        status="pending"
    )

    db.add(return_request)

    # -----------------------------------------------------
    # UPDATE ORDER
    # -----------------------------------------------------

    order.order_status = "Return Requested"

    db.commit()

    db.refresh(return_request)

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
            e
        )

    # -----------------------------------------------------
    # WEBSOCKET NOTIFICATION
    # -----------------------------------------------------

    notification_websocket_sent = False

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
            e
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

        "return_request": {

            "id":
                return_request.id,

            "order_id":
                return_request.order_id,

            "user_id":
                return_request.user_id,

            "reason":
                return_request.reason,

            "comment":
                return_request.comment,

            "status":
                return_request.status,

            "created_at":
                return_request.created_at
        },

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
# APPROVE RETURN
# =========================================================
#
# PUT /orders/returns/{return_id}/approve
# =========================================================

@router.put("/returns/{return_id}/approve")
async def approve_return(
    return_id: int,
    db: Session = Depends(get_db)
):

    print()
    print("=" * 70)
    print("APPROVE RETURN")
    print("Return Request ID:", return_id)
    print("=" * 70)

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

    if request.status.lower() != "pending":

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
        .first()
    )

    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    request.status = "approved"

    order.order_status = "Returned"

    db.commit()

    db.refresh(request)
    db.refresh(order)

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

    user = (
        db.query(User)
        .filter(
            User.id == request.user_id
        )
        .first()
    )

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
            e
        )

    notification_websocket_sent = False

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
            e
        )

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
            notification_websocket_sent
    }


# =========================================================
# REJECT RETURN
# =========================================================
#
# PUT /orders/returns/{return_id}/reject
# =========================================================

@router.put("/returns/{return_id}/reject")
async def reject_return(
    return_id: int,
    db: Session = Depends(get_db)
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
        .first()
    )

    if not request:

        raise HTTPException(
            status_code=404,
            detail="Return request not found"
        )

    if request.status.lower() != "pending":

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
        .first()
    )

    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    request.status = "rejected"

    order.order_status = "Delivered"

    db.commit()

    db.refresh(request)
    db.refresh(order)

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

    user = (
        db.query(User)
        .filter(
            User.id == request.user_id
        )
        .first()
    )

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
            e
        )

    notification_websocket_sent = False

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
            e
        )

    email_sent = send_order_email(
        user=user,
        order_id=order.id,
        subject=(
            f"Smart Ecommerce - "
            f"Return Rejected #{order.id}"
        ),
        message=notification_message
    )

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
#
# IMPORTANT:
# Keep this dynamic route AFTER all /orders/returns
# and /orders/analytics routes.
#
# GET /orders/{order_id}
# =========================================================

@router.get("/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db)
):

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

    return {

        "id":
            order.id,

        "user_id":
            order.user_id,

        "total_amount":
            order.total_amount,

        "payment_status":
            order.payment_status,

        "order_status":
            order.order_status,

        "status":
            order.order_status,

        "created_at":
            order.created_at
    }