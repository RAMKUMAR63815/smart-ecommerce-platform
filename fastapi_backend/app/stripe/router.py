import stripe

from fastapi import APIRouter, Request, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Order, Payment
from app.core.config import (
    STRIPE_SECRET_KEY,
    STRIPE_WEBHOOK_SECRET,
)


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
            detail="Missing Stripe signature",
        )

    # =====================================================
    # 3. VERIFY STRIPE EVENT
    # =====================================================

    try:

        event = stripe.Webhook.construct_event(
            payload,
            signature,
            STRIPE_WEBHOOK_SECRET,
        )

    except ValueError as e:

        print(
            "ERROR: Invalid payload:",
            repr(e)
        )

        raise HTTPException(
            status_code=400,
            detail="Invalid webhook payload",
        )

    except stripe.error.SignatureVerificationError as e:

        print(
            "ERROR: Invalid signature:",
            repr(e)
        )

        raise HTTPException(
            status_code=400,
            detail="Invalid Stripe signature",
        )

    except Exception as e:

        print(
            "ERROR: Webhook verification failed:",
            repr(e)
        )

        raise HTTPException(
            status_code=400,
            detail="Webhook verification failed",
        )

    # =====================================================
    # IMPORTANT
    # DO NOT USE:
    # event.get(...)
    # event.to_dict_recursive()
    #
    # Use Stripe object indexing:
    # event["type"]
    # =====================================================

    event_type = event["type"]

    print(
        "EVENT TYPE:",
        event_type
    )

    # =====================================================
    # 4. IGNORE NON-CHECKOUT EVENTS
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
    # 5. GET CHECKOUT SESSION
    # =====================================================

    session = event["data"]["object"]

    print("----------------------------------------")
    print("CHECKOUT SESSION")
    print("----------------------------------------")

    # StripeObject supports [] access
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
    # 6. GET METADATA
    # =====================================================

    if not metadata:

        print(
            "ERROR: Metadata is empty"
        )

        return {
            "received": True,
            "message": "Metadata missing"
        }

    # Stripe metadata behaves like a mapping
    order_id = metadata["order_id"] if "order_id" in metadata else None

    payment_id = metadata["payment_id"] if "payment_id" in metadata else None

    print(
        "Order ID:",
        order_id
    )

    print(
        "Payment ID:",
        payment_id
    )

    # =====================================================
    # 7. CHECK METADATA
    # =====================================================

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
    # 9. CHECK PAYMENT STATUS
    # =====================================================

    print(
        "Stripe payment status:",
        payment_status
    )

    if payment_status != "paid":

        print(
            "Payment is not completed yet"
        )

        return {
            "received": True,
            "message": "Payment not completed"
        }

    # =====================================================
    # 10. OPEN DATABASE
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
        # UPDATE PAYMENT
        # =================================================

        payment.status = "paid"

        payment.transaction_id = (
            payment_intent
            or session_id
        )

        # =================================================
        # UPDATE ORDER
        # =================================================

        order.payment_status = "paid"

        order.order_status = "confirmed"

        # =================================================
        # COMMIT DATABASE
        # =================================================

        print(
            "COMMITTING DATABASE..."
        )

        db.commit()

        db.refresh(order)

        db.refresh(payment)

        # =================================================
        # VERIFY
        # =================================================

        print("----------------------------------------")
        print("DATABASE UPDATED SUCCESSFULLY")
        print("----------------------------------------")

        print(
            "Order ID:",
            order.id
        )

        print(
            "Order payment_status:",
            order.payment_status
        )

        print(
            "Order order_status:",
            order.order_status
        )

        print(
            "Payment ID:",
            payment.id
        )

        print(
            "Payment status:",
            payment.status
        )

        print(
            "Transaction ID:",
            payment.transaction_id
        )

        print("----------------------------------------")

        return {
            "received": True,
            "message": "Payment updated successfully",
            "order_id": order.id,
            "payment_id": payment.id,
            "payment_status": payment.status,
            "order_status": order.order_status,
        }

    except Exception as e:

        db.rollback()

        print("----------------------------------------")
        print("DATABASE UPDATE ERROR")
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
            detail=f"Database update failed: {str(e)}",
        )

    finally:

        db.close()