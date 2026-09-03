import stripe

from fastapi import (
    APIRouter,
    Request,
    HTTPException
)

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
    STRIPE_WEBHOOK_SECRET
)

from app.websocket.websocket import (
    send_notification,
    send_order_update,
    send_payment_update
)

from app.services.email_service import send_email


# =========================================================
# STRIPE CONFIGURATION
# =========================================================

stripe.api_key = STRIPE_SECRET_KEY


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/stripe",
    tags=["Stripe"]
)


# =========================================================
# HELPER: SAFELY GET VALUE FROM STRIPE OBJECT
# =========================================================

def stripe_value(
    obj,
    key,
    default=None
):
    """
    Safely read a value from either:
    - dict
    - StripeObject
    """

    if obj is None:
        return default

    if isinstance(obj, dict):
        return obj.get(
            key,
            default
        )

    return getattr(
        obj,
        key,
        default
    )


# =========================================================
# HELPER: GET STRIPE OBJECT ID
# =========================================================

def stripe_object_id(
    obj
):
    """
    Extract Stripe object ID from:
    - string
    - dictionary
    - StripeObject
    """

    if obj is None:
        return None

    if isinstance(obj, str):
        return obj

    if isinstance(obj, dict):
        return obj.get("id")

    return getattr(
        obj,
        "id",
        None
    )


# =========================================================
# HELPER: GET PAYMENT INTENT ID
# =========================================================

def get_payment_intent_id(
    payment_intent
):
    """
    Convert Stripe PaymentIntent into
    a normal string ID.
    """

    payment_intent_id = stripe_object_id(
        payment_intent
    )

    if not payment_intent_id:
        return None

    payment_intent_id = str(
        payment_intent_id
    ).strip()

    return payment_intent_id


# =========================================================
# HELPER: VERIFY PAYMENT INTENT
# =========================================================

def verify_payment_intent(
    payment_intent_id: str
):
    """
    Retrieve and verify a Stripe PaymentIntent.
    """

    if not payment_intent_id:

        raise ValueError(
            "PaymentIntent ID is missing"
        )

    payment_intent_id = str(
        payment_intent_id
    ).strip()

    # -----------------------------------------------------
    # PAYMENT INTENT FORMAT
    # -----------------------------------------------------

    if not payment_intent_id.startswith("pi_"):

        raise ValueError(
            "Invalid Stripe PaymentIntent ID"
        )

    # -----------------------------------------------------
    # PLACEHOLDER PROTECTION
    # -----------------------------------------------------

    invalid_placeholders = {
        "pi_ACTUAL_ID",
        "pi_actual_id",
        "pi_YOUR_PAYMENT_INTENT_ID",
        "pi_your_payment_intent_id",
        "pi_REPLACE_ME",
        "pi_replace_me"
    }

    if payment_intent_id in invalid_placeholders:

        raise ValueError(
            "Placeholder PaymentIntent ID detected"
        )

    # -----------------------------------------------------
    # RETRIEVE FROM STRIPE
    # -----------------------------------------------------

    try:

        payment_intent = (
            stripe.PaymentIntent.retrieve(
                payment_intent_id
            )
        )

    except stripe.error.AuthenticationError as e:

        print(
            "STRIPE AUTHENTICATION ERROR:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Stripe authentication failed. "
                "Check STRIPE_SECRET_KEY."
            )
        )

    except stripe.error.InvalidRequestError as e:

        print(
            "INVALID STRIPE PAYMENTINTENT:",
            repr(e)
        )

        raise ValueError(
            "Stripe PaymentIntent does not exist"
        )

    except stripe.StripeError as e:

        print(
            "STRIPE PAYMENTINTENT ERROR:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Stripe PaymentIntent verification failed"
            )
        )

    # -----------------------------------------------------
    # VERIFY ID
    # -----------------------------------------------------

    verified_id = stripe_object_id(
        payment_intent
    )

    if not verified_id:

        raise ValueError(
            "Stripe returned no PaymentIntent ID"
        )

    if verified_id != payment_intent_id:

        raise ValueError(
            "PaymentIntent ID mismatch"
        )

    # -----------------------------------------------------
    # VERIFY STATUS
    # -----------------------------------------------------

    payment_intent_status = stripe_value(
        payment_intent,
        "status"
    )

    print(
        "Stripe PaymentIntent status:",
        payment_intent_status
    )

    if payment_intent_status != "succeeded":

        raise ValueError(
            "Stripe PaymentIntent is not successful. "
            f"Current status: {payment_intent_status}"
        )

    print(
        "PaymentIntent successfully verified:",
        verified_id
    )

    return payment_intent


# =========================================================
# HELPER: SEND PAYMENT EMAIL
# =========================================================

def send_payment_email(
    user: User,
    order_id: int,
    message: str
):

    if not user:

        print(
            f"Payment email skipped for order #{order_id}: "
            "User not found"
        )

        return False

    if not user.email:

        print(
            f"Payment email skipped for order #{order_id}: "
            "Email not available"
        )

        return False

    try:

        send_email(
            to_email=user.email,

            subject=(
                "Smart Ecommerce - "
                f"Payment Successful #{order_id}"
            ),

            body=message
        )

        print(
            f"Payment email sent for order #{order_id}"
        )

        return True

    except Exception as e:

        print(
            "Payment email failed:",
            repr(e)
        )

        return False


# =========================================================
# STRIPE WEBHOOK
# =========================================================

@router.post("/webhook")
async def stripe_webhook(
    request: Request
):

    print()
    print("=" * 70)
    print("STRIPE WEBHOOK RECEIVED")
    print("=" * 70)

    # =====================================================
    # 1. GET RAW REQUEST BODY
    # =====================================================

    payload = await request.body()

    print(
        "Payload length:",
        len(payload)
    )

    # =====================================================
    # 2. GET STRIPE SIGNATURE
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
    # 3. VERIFY WEBHOOK
    # =====================================================

    try:

        event = stripe.Webhook.construct_event(
            payload,
            signature,
            STRIPE_WEBHOOK_SECRET
        )

        if hasattr(
            event,
            "to_dict"
        ):

            event = event.to_dict()

    except ValueError as e:

        print(
            "ERROR: Invalid webhook payload:",
            repr(e)
        )

        raise HTTPException(
            status_code=400,
            detail="Invalid webhook payload"
        )

    except stripe.error.SignatureVerificationError as e:

        print(
            "ERROR: Invalid Stripe signature:",
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
    # 4. GET EVENT INFORMATION
    # =====================================================

    event_type = stripe_value(
        event,
        "type"
    )

    event_id = stripe_value(
        event,
        "id"
    )

    print(
        "EVENT TYPE:",
        event_type
    )

    print(
        "EVENT ID:",
        event_id
    )

    # =====================================================
    # 5. PROCESS CHECKOUT COMPLETED
    # =====================================================

    if event_type != "checkout.session.completed":

        print(
            "Ignoring Stripe event:",
            event_type
        )

        return {
            "received": True,
            "message": "Event ignored",
            "event_type": event_type
        }

    # =====================================================
    # 6. GET EVENT DATA
    # =====================================================

    event_data = stripe_value(
        event,
        "data",
        {}
    )

    if not event_data:

        print(
            "ERROR: Event data missing"
        )

        return {
            "received": True,
            "message": "Event data missing"
        }

    # =====================================================
    # 7. GET CHECKOUT SESSION
    # =====================================================

    session = stripe_value(
        event_data,
        "object",
        {}
    )

    if not session:

        print(
            "ERROR: Checkout session missing"
        )

        return {
            "received": True,
            "message": "Checkout session missing"
        }

    # =====================================================
    # 8. GET SESSION DATA
    # =====================================================

    session_id = stripe_object_id(
        session
    )

    payment_status = stripe_value(
        session,
        "payment_status"
    )

    payment_intent_object = stripe_value(
        session,
        "payment_intent"
    )

    metadata = stripe_value(
        session,
        "metadata",
        {}
    )

    if not metadata:

        metadata = {}

    print()
    print("-" * 70)
    print("STRIPE CHECKOUT SESSION")
    print("-" * 70)

    print(
        "Checkout Session ID:",
        session_id
    )

    print(
        "Payment Status:",
        payment_status
    )

    print(
        "Payment Intent:",
        payment_intent_object
    )

    print(
        "Metadata:",
        metadata
    )

    # =====================================================
    # 9. VERIFY CHECKOUT SESSION
    # =====================================================

    if not session_id:

        print(
            "ERROR: Checkout Session ID missing"
        )

        return {
            "received": True,
            "message": "Checkout Session ID missing"
        }

    if not str(
        session_id
    ).startswith("cs_"):

        print(
            "ERROR: Invalid Checkout Session ID:",
            session_id
        )

        return {
            "received": True,
            "message": "Invalid Checkout Session ID"
        }

    # =====================================================
    # 10. VERIFY PAYMENT STATUS
    # =====================================================

    if payment_status != "paid":

        print(
            "Stripe payment is not completed:",
            payment_status
        )

        return {
            "received": True,
            "message": "Payment not completed",
            "payment_status": payment_status
        }

    # =====================================================
    # 11. GET PAYMENT INTENT ID
    # =====================================================

    payment_intent_id = get_payment_intent_id(
        payment_intent_object
    )

    if not payment_intent_id:

        print(
            "ERROR: Stripe PaymentIntent ID missing"
        )

        return {
            "received": True,
            "message": (
                "Stripe PaymentIntent ID missing"
            ),
            "checkout_session_id": session_id
        }

    print(
        "PaymentIntent ID from webhook:",
        payment_intent_id
    )

    # =====================================================
    # 12. VERIFY PAYMENT INTENT
    # =====================================================

    try:

        verified_payment_intent = (
            verify_payment_intent(
                payment_intent_id
            )
        )

    except ValueError as e:

        print(
            "PaymentIntent validation failed:",
            str(e)
        )

        return {
            "received": True,
            "message": str(e),
            "payment_intent": payment_intent_id
        }

    # =====================================================
    # 13. GET ORDER ID
    # =====================================================

    order_id_value = metadata.get(
        "order_id"
    )

    if not order_id_value:

        print(
            "ERROR: order_id missing from metadata"
        )

        return {
            "received": True,
            "message": (
                "order_id missing from metadata"
            )
        }

    # =====================================================
    # 14. GET USER ID
    # =====================================================

    user_id_value = metadata.get(
        "user_id"
    )

    # user_id is optional because the Order
    # already contains user_id.
    #
    # =====================================================

    # =====================================================
    # 15. CONVERT ORDER / USER IDS
    # =====================================================

    try:

        order_id = int(
            order_id_value
        )

        user_id = (
            int(user_id_value)
            if user_id_value
            else None
        )

    except (
        ValueError,
        TypeError
    ) as e:

        print(
            "ERROR: Invalid metadata IDs:",
            repr(e)
        )

        return {
            "received": True,
            "message": "Invalid order/user ID"
        }

    print(
        "Order ID:",
        order_id
    )

    print(
        "User ID:",
        user_id
    )

    # =====================================================
    # 16. DATABASE SESSION
    # =====================================================

    db: Session = SessionLocal()

    try:

        print()
        print("-" * 70)
        print("DATABASE PROCESSING")
        print("-" * 70)

        # =================================================
        # FIND ORDER
        # =================================================

        order = (
            db.query(Order)
            .filter(
                Order.id == order_id
            )
            .with_for_update()
            .first()
        )

        if not order:

            print(
                "ERROR: Order not found:",
                order_id
            )

            return {
                "received": True,
                "message": "Order not found",
                "order_id": order_id
            }

        print(
            "ORDER FOUND:",
            order.id
        )

        # =================================================
        # VERIFY USER
        # =================================================

        if (
            user_id is not None
            and order.user_id != user_id
        ):

            print(
                "ERROR: Metadata user_id does not "
                "match order user_id"
            )

            raise HTTPException(
                status_code=400,
                detail=(
                    "User does not belong "
                    "to the specified order"
                )
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
        # GET STRIPE AMOUNT
        # =================================================

        stripe_amount = stripe_value(
            verified_payment_intent,
            "amount"
        )

        if stripe_amount is None:

            print(
                "ERROR: Stripe amount missing"
            )

            raise HTTPException(
                status_code=400,
                detail="Stripe payment amount is missing"
            )

        stripe_amount = int(
            stripe_amount
        )

        stripe_amount_normal = (
            stripe_amount / 100
        )

        print(
            "Stripe amount in paise:",
            stripe_amount
        )

        print(
            "Stripe amount in INR:",
            stripe_amount_normal
        )

        # =================================================
        # FIND PAYMENT BY ORDER ID
        # =================================================
        #
        # IMPORTANT:
        #
        # We NO LONGER depend on payment_id
        # from Stripe metadata.
        #
        # This solves the problem where:
        #
        # Order exists
        # Payment does not exist
        #
        # =================================================

        payment = (
            db.query(Payment)
            .filter(
                Payment.order_id == order.id
            )
            .order_by(
                Payment.id.desc()
            )
            .with_for_update()
            .first()
        )

        # =================================================
        # CREATE PAYMENT IF MISSING
        # =================================================

        if not payment:

            print()
            print(
                "NO PAYMENT RECORD FOUND"
            )

            print(
                "Creating Payment record..."
            )

            payment = Payment(

                order_id=order.id,

                amount=stripe_amount_normal,

                payment_method="stripe",

                transaction_id=payment_intent_id,

                status="Paid"
            )

            db.add(
                payment
            )

            # Get Payment.id before commit
            db.flush()

            print(
                "NEW PAYMENT CREATED:",
                payment.id
            )

        else:

            print()
            print(
                "PAYMENT FOUND:",
                payment.id
            )

        # =================================================
        # VERIFY PAYMENT BELONGS TO ORDER
        # =================================================

        if payment.order_id != order.id:

            print(
                "ERROR: Payment does not belong to order"
            )

            raise HTTPException(
                status_code=400,
                detail=(
                    "Payment does not belong "
                    "to the specified order"
                )
            )

        # =================================================
        # VERIFY EXISTING PAYMENT AMOUNT
        # =================================================

        if payment.amount is not None:

            expected_stripe_amount = int(
                round(
                    float(payment.amount) * 100
                )
            )

            print(
                "Database payment amount:",
                payment.amount
            )

            print(
                "Expected Stripe amount:",
                expected_stripe_amount
            )

            print(
                "Actual Stripe amount:",
                stripe_amount
            )

            if (
                expected_stripe_amount
                != stripe_amount
            ):

                print(
                    "ERROR: Payment amount mismatch"
                )

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Stripe payment amount does not "
                        "match database payment amount"
                    )
                )

        else:

            # Payment exists but amount is NULL.
            # Fill it from verified Stripe amount.

            payment.amount = (
                stripe_amount_normal
            )

        # =================================================
        # DUPLICATE WEBHOOK PROTECTION
        # =================================================

        already_paid = (
            str(
                order.payment_status or ""
            ).lower()
            == "paid"
            and
            str(
                payment.status or ""
            ).lower()
            == "paid"
        )

        if already_paid:

            print(
                f"Order #{order.id} is already paid."
            )

            # -------------------------------------------------
            # ALWAYS CORRECT PAYMENT METHOD
            # -------------------------------------------------

            payment.payment_method = "stripe"

            # -------------------------------------------------
            # ALWAYS STORE REAL PAYMENT INTENT
            # -------------------------------------------------

            if (
                payment.transaction_id
                != payment_intent_id
            ):

                print(
                    "Correcting transaction_id"
                )

                print(
                    "Old:",
                    payment.transaction_id
                )

                print(
                    "New:",
                    payment_intent_id
                )

                payment.transaction_id = (
                    payment_intent_id
                )

                db.commit()

                db.refresh(
                    payment
                )

            else:

                db.commit()

            return {

                "received":
                    True,

                "message":
                    "Payment already processed",

                "order_id":
                    order.id,

                "payment_id":
                    payment.id,

                "payment_status":
                    order.payment_status,

                "order_status":
                    order.order_status,

                "checkout_session_id":
                    session_id,

                "transaction_id":
                    payment.transaction_id
            }

        # =================================================
        # UPDATE PAYMENT
        # =================================================

        payment.status = "Paid"

        payment.payment_method = "stripe"

        payment.transaction_id = (
            payment_intent_id
        )

        # =================================================
        # UPDATE ORDER
        # =================================================

        order.payment_status = "Paid"

        order.order_status = "Confirmed"

        # =================================================
        # COMMIT PAYMENT + ORDER
        # =================================================

        db.commit()

        db.refresh(
            order
        )

        db.refresh(
            payment
        )

        print()
        print("-" * 70)
        print("PAYMENT DATABASE UPDATED")
        print("-" * 70)

        print(
            "Order ID:",
            order.id
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

        print(
            "Transaction ID:",
            payment.transaction_id
        )

        # =================================================
        # DATABASE NOTIFICATION
        # =================================================

        notification = None

        notification_message = (
            f"Payment successful for order #{order.id}."
        )

        try:

            notification = Notification(

                user_id=order.user_id,

                type="payment",

                message=notification_message,

                read_status=False
            )

            db.add(
                notification
            )

            db.commit()

            db.refresh(
                notification
            )

            print(
                "Database notification created:",
                notification.id
            )

        except Exception as e:

            db.rollback()

            print(
                "Database notification failed:",
                repr(e)
            )

        # =================================================
        # WEBSOCKET ORDER UPDATE
        # =================================================

        websocket_sent = False

        try:

            websocket_sent = (
                await send_order_update(

                    user_id=order.user_id,

                    order_id=order.id,

                    status=order.order_status
                )
            )

            print(
                "Stripe order WebSocket result:",
                websocket_sent
            )

        except Exception as e:

            print(
                "Stripe order WebSocket failed:",
                repr(e)
            )

        # =================================================
        # WEBSOCKET PAYMENT UPDATE
        # =================================================

        payment_websocket_sent = False

        try:

            payment_websocket_sent = (
                await send_payment_update(

                    user_id=order.user_id,

                    order_id=order.id,

                    payment_status=order.payment_status
                )
            )

            print(
                "Stripe payment WebSocket result:",
                payment_websocket_sent
            )

        except Exception as e:

            print(
                "Stripe payment WebSocket failed:",
                repr(e)
            )

        # =================================================
        # WEBSOCKET NOTIFICATION
        # =================================================

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

                print(
                    "Stripe notification WebSocket result:",
                    notification_websocket_sent
                )

            except Exception as e:

                print(
                    "Stripe notification WebSocket failed:",
                    repr(e)
                )

        # =================================================
        # EMAIL
        # =================================================

        email_sent = send_payment_email(

            user=user,

            order_id=order.id,

            message=notification_message
        )

        if email_sent:

            print(
                "Stripe payment email sent successfully"
            )

        # =================================================
        # FINAL RESPONSE
        # =================================================

        print()
        print("=" * 70)
        print("STRIPE PAYMENT PROCESS COMPLETED")
        print("=" * 70)

        return {

            "received":
                True,

            "message":
                "Payment updated successfully",

            "event_type":
                event_type,

            "event_id":
                event_id,

            "order_id":
                order.id,

            "payment_id":
                payment.id,

            "payment_amount":
                payment.amount,

            "payment_method":
                payment.payment_method,

            "payment_status":
                payment.status,

            "order_payment_status":
                order.payment_status,

            "order_status":
                order.order_status,

            "checkout_session_id":
                session_id,

            "transaction_id":
                payment.transaction_id,

            "notification_id":
                (
                    notification.id
                    if notification
                    else None
                ),

            "websocket_sent":
                websocket_sent,

            "payment_websocket_sent":
                payment_websocket_sent,

            "notification_websocket_sent":
                notification_websocket_sent,

            "email_sent":
                email_sent
        }

    # =====================================================
    # HTTP EXCEPTION
    # =====================================================

    except HTTPException:

        db.rollback()

        raise

    # =====================================================
    # GENERAL DATABASE ERROR
    # =====================================================

    except Exception as e:

        db.rollback()

        print()
        print("-" * 70)
        print("STRIPE DATABASE UPDATE ERROR")
        print("-" * 70)

        print(
            "ERROR TYPE:",
            type(e).__name__
        )

        print(
            "ERROR:",
            repr(e)
        )

        print("-" * 70)

        raise HTTPException(
            status_code=500,
            detail=(
                "Database update failed: "
                f"{str(e)}"
            )
        )

    # =====================================================
    # CLOSE DATABASE
    # =====================================================

    finally:

        db.close()