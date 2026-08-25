from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Order, Payment, User, Notification

from app.websocket.websocket import (
    send_notification,
    send_order_update
)

from app.services.email_service import send_email


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/payment",
    tags=["Payment"]
)


# =========================================================
# DATABASE SESSION
# =========================================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# =========================================================
# GET PAYMENT / ORDER DETAILS
# =========================================================

@router.get("/{order_id}")
def get_payment_order(
    order_id: int,
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # FIND ORDER
    # -----------------------------------------------------

    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .first()
    )

    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order Not Found"
        )

    # -----------------------------------------------------
    # FIND PAYMENT
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
    # RESPONSE
    # -----------------------------------------------------

    return {

        "order": {

            "id": order.id,

            "user_id": order.user_id,

            "total_amount": order.total_amount,

            "payment_status":
                order.payment_status,

            "order_status":
                order.order_status,

            "status":
                order.order_status,

            "created_at":
                order.created_at
        },

        "payment": {

            "id":
                payment.id
                if payment
                else None,

            "amount":
                payment.amount
                if payment
                else None,

            "payment_method":
                payment.payment_method
                if payment
                else None,

            "transaction_id":
                payment.transaction_id
                if payment
                else None,

            "status":
                payment.status
                if payment
                else None,

            "timestamp":
                payment.timestamp
                if payment
                else None
        }
    }


# =========================================================
# PAYMENT FAILURE
# =========================================================

@router.put("/{order_id}/failed")
async def payment_failed(
    order_id: int,
    db: Session = Depends(get_db)
):

    print()
    print("=" * 70)
    print("PAYMENT FAILURE")
    print("Order ID:", order_id)
    print("=" * 70)

    # -----------------------------------------------------
    # FIND ORDER
    # -----------------------------------------------------

    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .first()
    )

    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order Not Found"
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
    # FIND PAYMENT
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
    # UPDATE PAYMENT STATUS
    # -----------------------------------------------------

    order.payment_status = "Failed"

    # Keep order status as Pending.
    # Payment failed does not mean the order is confirmed.

    order.order_status = "Pending"

    if payment:

        payment.status = "Failed"

    db.commit()

    db.refresh(order)

    if payment:
        db.refresh(payment)

    print(
        "Order #",
        order.id,
        "payment status:",
        order.payment_status
    )

    print(
        "Order #",
        order.id,
        "order status:",
        order.order_status
    )

    # =====================================================
    # DATABASE NOTIFICATION
    # =====================================================

    notification_message = (
        f"Payment failed for order #{order.id}."
    )

    notification = Notification(
        user_id=order.user_id,
        type="payment",
        message=notification_message,
        read_status=False
    )

    db.add(notification)

    db.commit()

    db.refresh(notification)

    print(
        "Database notification created"
    )

    print(
        "Notification ID:",
        notification.id
    )

    # =====================================================
    # WEBSOCKET NOTIFICATION
    # =====================================================

    try:

        websocket_result = await send_notification(

            user_id=order.user_id,

            notification_type="payment",

            message=notification_message,

            notification_id=notification.id

        )

        print(
            "Payment failure WebSocket result:",
            websocket_result
        )

    except Exception as e:

        print(
            "Payment failure WebSocket failed:",
            e
        )

    # =====================================================
    # WEBSOCKET ORDER UPDATE
    # =====================================================

    try:

        order_websocket_result = await send_order_update(

            user_id=order.user_id,

            order_id=order.id,

            status=order.order_status

        )

        print(
            "Payment failure order WebSocket result:",
            order_websocket_result
        )

    except Exception as e:

        print(
            "Payment failure order WebSocket failed:",
            e
        )

    # =====================================================
    # EMAIL
    # =====================================================

    email_sent = False

    if user and user.email:

        try:

            send_email(

                to_email=user.email,

                subject=(
                    "Smart Ecommerce - "
                    f"Payment Failed #{order.id}"
                ),

                body=notification_message

            )

            email_sent = True

            print(
                "Payment failure email sent successfully"
            )

        except Exception as e:

            print(
                "Payment failure email failed:",
                e
            )

    # =====================================================
    # RESPONSE
    # =====================================================

    return {

        "message":
            "Payment failed notification sent",

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

        "payment": {

            "id":
                payment.id
                if payment
                else None,

            "status":
                payment.status
                if payment
                else "Failed"
        },

        "notification": {

            "id":
                notification.id,

            "type":
                notification.type,

            "message":
                notification.message,

            "read_status":
                notification.read_status
        },

        "email_sent":
            email_sent
    }