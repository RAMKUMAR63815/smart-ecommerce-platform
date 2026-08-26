from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from sqlalchemy import func

from app.database import get_db

from app.models import (
    Order,
    OrderItem,
    Cart,
    Product,
    User,
    Notification
)

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


    # =====================================================
    # CREATE ORDER ITEMS
    # =====================================================
    #
    # IMPORTANT:
    #
    # Cart items will be deleted later.
    #
    # Therefore we permanently save:
    #
    # order_id
    # product_id
    # quantity
    # price
    #
    # This allows analytics to calculate:
    #
    # Top-selling products
    # Product quantity sold
    # Product sales
    #
    # =====================================================

    for item, product in products:

        order_item = OrderItem(

            order_id=order.id,

            product_id=product.id,

            quantity=item.quantity,

            price=product.price
        )

        db.add(order_item)


    db.commit()


    print(
        f"Order items created for order #{order.id}"
    )


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


    # =====================================================
    # DATABASE NOTIFICATION
    # =====================================================

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


    print(
        f"Database notification created: "
        f"#{notification.id}"
    )


    # =====================================================
    # WEBSOCKET ORDER UPDATE
    # =====================================================

    websocket_sent = False

    try:

        websocket_sent = await send_order_update(

            user_id=user_id,

            order_id=order.id,

            status=order.order_status
        )

        print(
            "Create order WebSocket result:",
            websocket_sent
        )

    except Exception as e:

        print(
            "Create order WebSocket failed:",
            e
        )


    # =====================================================
    # WEBSOCKET NOTIFICATION
    # =====================================================

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

        print(
            "Create order notification WebSocket result:",
            notification_websocket_sent
        )

    except Exception as e:

        print(
            "Create order notification WebSocket failed:",
            e
        )


    # =====================================================
    # EMAIL
    # =====================================================

    email_sent = send_order_email(

        user=user,

        order_id=order.id,

        subject=(
            f"Smart Ecommerce - "
            f"Order #{order.id} Created"
        ),

        message=notification_message
    )


    # =====================================================
    # RESPONSE
    # =====================================================

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
# GET SINGLE ORDER
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


    print(
        "Order user ID:",
        order.user_id
    )


    # -----------------------------------------------------
    # ALREADY PAID
    # -----------------------------------------------------

    if order.payment_status == "Paid":

        print(
            f"Order #{order.id} is already paid"
        )

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


    # -----------------------------------------------------
    # UPDATE PAYMENT
    # -----------------------------------------------------

    order.payment_status = "Paid"

    order.order_status = "Confirmed"


    db.commit()

    db.refresh(order)


    print(
        f"Order #{order.id} updated:"
    )

    print(
        "Payment Status:",
        order.payment_status
    )

    print(
        "Order Status:",
        order.order_status
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


    print(
        "User email:",
        user.email
    )


    # =====================================================
    # DATABASE NOTIFICATION
    # =====================================================

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


    print()
    print(
        "Database notification created"
    )

    print(
        "Notification ID:",
        notification.id
    )


    # =====================================================
    # WEBSOCKET ORDER UPDATE
    # =====================================================

    websocket_sent = False


    try:

        websocket_sent = await send_order_update(

            user_id=order.user_id,

            order_id=order.id,

            status=order.order_status
        )


        print(
            "Payment order WebSocket result:",
            websocket_sent
        )


    except Exception as e:

        print(
            "Payment order WebSocket failed:",
            e
        )


    # =====================================================
    # WEBSOCKET NOTIFICATION
    # =====================================================

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


        print(
            "Payment notification WebSocket result:",
            notification_websocket_sent
        )


    except Exception as e:

        print(
            "Payment notification WebSocket failed:",
            e
        )


    # =====================================================
    # EMAIL
    # =====================================================

    email_sent = send_order_email(

        user=user,

        order_id=order.id,

        subject=(

            f"Smart Ecommerce - "
            f"Payment Successful #{order.id}"
        ),

        message=notification_message
    )


    # =====================================================
    # FINAL RESPONSE
    # =====================================================

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

        "Shipped",

        "Delivered",

        "Cancelled"
    ]


    if status not in valid_statuses:

        raise HTTPException(

            status_code=400,

            detail=(
                "Invalid status. "
                "Use: Pending, Confirmed, Shipped, "
                "Delivered, or Cancelled"
            )
        )


    # -----------------------------------------------------
    # UPDATE STATUS
    # -----------------------------------------------------

    order.order_status = status


    db.commit()

    db.refresh(order)


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


    # =====================================================
    # DATABASE NOTIFICATION
    # =====================================================

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


    print(
        "Database notification created:",
        notification.id
    )


    # =====================================================
    # WEBSOCKET ORDER UPDATE
    # =====================================================

    websocket_sent = False


    try:

        websocket_sent = await send_order_update(

            user_id=order.user_id,

            order_id=order.id,

            status=order.order_status
        )


        print(
            "Status WebSocket result:",
            websocket_sent
        )


    except Exception as e:

        print(
            "Status WebSocket failed:",
            e
        )


    # =====================================================
    # WEBSOCKET NOTIFICATION
    # =====================================================

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


        print(
            "Status notification WebSocket result:",
            notification_websocket_sent
        )


    except Exception as e:

        print(
            "Status notification WebSocket failed:",
            e
        )


    # =====================================================
    # EMAIL MESSAGE
    # =====================================================

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


    elif status == "Pending":

        email_message = (

            f"Your order #{order.id} "
            "is now pending."
        )


    else:

        email_message = notification_message


    # =====================================================
    # EMAIL
    # =====================================================

    email_sent = send_order_email(

        user=user,

        order_id=order.id,

        subject=(

            f"Smart Ecommerce - "
            f"Order #{order.id} {status}"
        ),

        message=email_message
    )


    # =====================================================
    # RESPONSE
    # =====================================================

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
# Returns the products with the highest quantity sold.
#
# Only PAID orders are included.
#
# Example response:
#
# [
#   {
#       "product_id": 1,
#       "product_name": "Laptop",
#       "quantity_sold": 25
#   }
# ]
#
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