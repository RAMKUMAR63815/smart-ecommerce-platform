import stripe

from fastapi import APIRouter, Request, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal

from app.models import (
    Order,
    Payment,
    User,
    Notification
)

from app.core.config import (
    STRIPE_SECRET_KEY,
    STRIPE_WEBHOOK_SECRET,
)

from app.websocket.websocket import (
    send_notification,
    send_order_update
)

from app.services.email_service import send_email


# =========================================================
# STRIPE CONFIG
# =========================================================

stripe.api_key = STRIPE_SECRET_KEY


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/stripe",
    tags=["Stripe"],
)


# =========================================================
# STRIPE WEBHOOK
# =========================================================

@router.post("/webhook")
async def stripe_webhook(request: Request):

    print("\n========================================")
    print("STRIPE WEBHOOK RECEIVED")
    print("========================================")

    # =====================================================
    # 1. RAW BODY
    # =====================================================

    payload = await request.body()

    print(
        "Payload length:",
        len(payload)
    )

    # =====================================================
    # 2. STRIPE SIGNATURE
    # =====================================================

    signature = request.headers.get(
        "stripe-signature"
    )

    if not signature:

        print(
            "ERROR: Missing Stripe signature"
        )

        raise HTTPException(
            status_code=400,
            detail="Missing Stripe signature"
        )

    # =====================================================
    # 3. VERIFY STRIPE EVENT
    # =====================================================

    try:

        event = stripe.Webhook.construct_event(
            payload,
            signature,
            STRIPE_WEBHOOK_SECRET
        )

    except ValueError as e:

        print(
            "ERROR: Invalid payload:",
            repr(e)
        )

        raise HTTPException(
            status_code=400,
            detail="Invalid webhook payload"
        )

    except stripe.error.SignatureVerificationError as e:

        print(
            "ERROR: Invalid signature:",
            repr(e)
        )

        raise HTTPException(
            status_code=400,
            detail="Invalid Stripe signature"
        )

    except Exception as e:

        print(
            "ERROR: Webhook verification failed:",
            repr(e)
        )

        raise HTTPException(
            status_code=400,
            detail="Webhook verification failed"
        )

    # =====================================================
    # 4. EVENT TYPE
    # =====================================================

    event_type = event["type"]

    print(
        "EVENT TYPE:",
        event_type
    )

    # =====================================================
    # 5. IGNORE OTHER EVENTS
    # =====================================================

    if event_type != "checkout.session.completed":

        print(
            "Ignoring event:",
            event_type
        )

        return {
            "received": True
        }

    # =====================================================
    # 6. CHECKOUT SESSION
    # =====================================================

    session = event["data"]["object"]

    print("----------------------------------------")
    print("CHECKOUT SESSION")
    print("----------------------------------------")

    session_id = session["id"]

    payment_status = session["payment_status"]

    payment_intent = session["payment_intent"]

    metadata = session["metadata"]

    print(
        "Session ID:",
        session_id
    )

    print(
        "Payment Status:",
        payment_status
    )

    print(
        "Payment Intent:",
        payment_intent
    )

    print(
        "Metadata:",
        metadata
    )

    # =====================================================
    # 7. CHECK METADATA
    # =====================================================

    if not metadata:

        print(
            "ERROR: Metadata is empty"
        )

        return {
            "received": True,
            "message": "Metadata missing"
        }

    order_id = (
        metadata["order_id"]
        if "order_id" in metadata
        else None
    )

    payment_id = (
        metadata["payment_id"]
        if "payment_id" in metadata
        else None
    )

    print(
        "Order ID:",
        order_id
    )

    print(
        "Payment ID:",
        payment_id
    )

    if not order_id:

        print(
            "ERROR: order_id missing"
        )

        return {
            "received": True,
            "message": "order_id missing"
        }

    if not payment_id:

        print(
            "ERROR: payment_id missing"
        )

        return {
            "received": True,
            "message": "payment_id missing"
        }

    # =====================================================
    # 8. CONVERT IDS
    # =====================================================

    try:

        order_id = int(order_id)

        payment_id = int(payment_id)

    except (ValueError, TypeError) as e:

        print(
            "ERROR: Invalid order/payment ID:",
            repr(e)
        )

        return {
            "received": True,
            "message": "Invalid order/payment ID"
        }

    # =====================================================
    # 9. PAYMENT STATUS
    # =====================================================

    if payment_status != "paid":

        print(
            "Payment is not completed:",
            payment_status
        )

        return {
            "received": True,
            "message": "Payment not completed"
        }

    # =====================================================
    # 10. DATABASE
    # =====================================================

    db: Session = SessionLocal()

    try:

        print("----------------------------------------")
        print("DATABASE UPDATE")
        print("----------------------------------------")

        # =================================================
        # FIND ORDER
        # =================================================

        order = (
            db.query(Order)
            .filter(
                Order.id == order_id
            )
            .first()
        )

        if not order:

            print(
                "ERROR: Order not found:",
                order_id
            )

            return {
                "received": True,
                "message": "Order not found"
            }

        print(
            "ORDER FOUND:",
            order.id
        )

        # =================================================
        # FIND PAYMENT
        # =================================================

        payment = (
            db.query(Payment)
            .filter(
                Payment.id == payment_id
            )
            .first()
        )

        if not payment:

            print(
                "ERROR: Payment not found:",
                payment_id
            )

            return {
                "received": True,
                "message": "Payment not found"
            }

        print(
            "PAYMENT FOUND:",
            payment.id
        )

        # =================================================
        # GET USER
        # =================================================

        user = (
            db.query(User)
            .filter(
                User.id == order.user_id
            )
            .first()
        )

        # =================================================
        # PREVENT DUPLICATE WEBHOOK PROCESSING
        # =================================================

        already_paid = (
            order.payment_status == "Paid"
            and payment.status == "Paid"
        )

        if already_paid:

            print(
                f"Order #{order.id} is already marked as paid."
            )

            return {
                "received": True,
                "message": "Payment already processed",
                "order_id": order.id,
                "payment_id": payment.id
            }

        # =================================================
        # UPDATE PAYMENT
        # =================================================

        payment.status = "Paid"

        payment.transaction_id = (
            payment_intent
            or session_id
        )

        # =================================================
        # UPDATE ORDER
        # =================================================

        # IMPORTANT:
        # Keep same capitalization used
        # by your existing /payment/{order_id}/pay
        # endpoint.

        order.payment_status = "Paid"

        order.order_status = "Confirmed"

        # =================================================
        # COMMIT PAYMENT / ORDER
        # =================================================

        db.commit()

        db.refresh(order)

        db.refresh(payment)

        print("----------------------------------------")
        print("DATABASE PAYMENT UPDATED")
        print("----------------------------------------")

        print(
            "Order ID:",
            order.id
        )

        print(
            "Payment Status:",
            order.payment_status
        )

        print(
            "Order Status:",
            order.order_status
        )

        print(
            "Payment ID:",
            payment.id
        )

        print(
            "Payment Status:",
            payment.status
        )

        print(
            "Transaction ID:",
            payment.transaction_id
        )

        # =================================================
        # DATABASE NOTIFICATION
        # =================================================

        notification_message = (
            f"Payment successful for order #{order.id}."
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
            "Database notification created:",
            notification.id
        )

        # =================================================
        # WEBSOCKET ORDER UPDATE
        # =================================================

        websocket_sent = False

        try:

            websocket_sent = await send_order_update(
                user_id=order.user_id,
                order_id=order.id,
                status=order.order_status
            )

            print(
                "Stripe order WebSocket result:",
                websocket_sent
            )

        except Exception as e:

            print(
                "Stripe order WebSocket failed:",
                e
            )

        # =================================================
        # WEBSOCKET NOTIFICATION
        # =================================================

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
                "Stripe notification WebSocket result:",
                notification_websocket_sent
            )

        except Exception as e:

            print(
                "Stripe notification WebSocket failed:",
                e
            )

        # =================================================
        # EMAIL
        # =================================================

        email_sent = False

        if user and user.email:

            try:

                send_email(
                    to_email=user.email,
                    subject=(
                        "Smart Ecommerce - "
                        f"Payment Successful #{order.id}"
                    ),
                    body=notification_message
                )

                email_sent = True

                print(
                    "Stripe payment email sent successfully"
                )

            except Exception as e:

                print(
                    "Stripe payment email failed:",
                    e
                )

        # =================================================
        # FINAL RESPONSE
        # =================================================

        print("----------------------------------------")
        print("STRIPE PAYMENT PROCESS COMPLETED")
        print("----------------------------------------")

        return {

            "received": True,

            "message":
                "Payment updated successfully",

            "order_id":
                order.id,

            "payment_id":
                payment.id,

            "payment_status":
                order.payment_status,

            "order_status":
                order.order_status,

            "notification_id":
                notification.id,

            "websocket_sent":
                websocket_sent,

            "notification_websocket_sent":
                notification_websocket_sent,

            "email_sent":
                email_sent
        }

    except Exception as e:

        db.rollback()

        print("----------------------------------------")
        print("STRIPE DATABASE UPDATE ERROR")
        print("----------------------------------------")

        print(
            "ERROR TYPE:",
            type(e).__name__
        )

        print(
            "ERROR:",
            repr(e)
        )

        print("----------------------------------------")

        raise HTTPException(
            status_code=500,
            detail=(
                "Database update failed: "
                f"{str(e)}"
            )
        )

    finally:

        db.close()