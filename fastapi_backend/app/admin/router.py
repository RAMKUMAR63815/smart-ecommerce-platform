from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

import stripe

from app.database import get_db

from app.models import (
    User,
    Product,
    Order,
    OrderItem,
    Payment,
    Notification,
    ReturnRequest,
)

from app.dependencies import (
    get_current_user,
    require_role,
)

from app.services.email_service import send_email

from app.websocket.websocket import (
    send_order_update,
    send_payment_update,
    send_notification,
)

from app.core.config import STRIPE_SECRET_KEY


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


# =========================================================
# STRIPE CONFIGURATION
# =========================================================

stripe.api_key = STRIPE_SECRET_KEY


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def normalize_status(value):
    """
    Normalize status values safely.

    Example:
        Approved
        approved
        APPROVED
        " Approved "

    All become:
        approved
    """

    if value is None:
        return ""

    return str(value).strip().lower()


def stripe_value(obj, key, default=None):
    """
    Safely read a value from either:

    - dictionary
    - StripeObject
    - normal Python object
    """

    if obj is None:
        return default

    if isinstance(obj, dict):
        return obj.get(key, default)

    try:
        return getattr(obj, key, default)

    except Exception:
        return default


def stripe_id(value):
    """
    Safely extract Stripe ID from:

    - string
    - dictionary
    - StripeObject
    """

    if value is None:
        return None

    if isinstance(value, str):
        return value

    if isinstance(value, dict):
        return value.get("id")

    try:
        return getattr(value, "id", None)

    except Exception:
        return None


def stripe_object_to_dict(obj):
    """
    Convert StripeObject into dictionary when possible.

    This prevents errors such as:

        'get' is a dict method, but an Event is not a dict
    """

    if obj is None:
        return None

    if isinstance(obj, dict):
        return obj

    try:
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
    except Exception:
        pass

    return obj


def stripe_amount_to_major(amount, currency):
    """
    Stripe stores money in smallest currency units.

    Example:

        Database:
            387036.46 INR

        Stripe:
            38703646

    This converts Stripe amount back to database amount.
    """

    if amount is None:
        return None

    currency = normalize_status(currency or "inr")

    zero_decimal_currencies = {
        "bif",
        "clp",
        "djf",
        "gnf",
        "jpy",
        "kmf",
        "krw",
        "mga",
        "pyg",
        "rwf",
        "ugx",
        "vnd",
        "vuv",
        "xaf",
        "xof",
        "xpf",
    }

    if currency in zero_decimal_currencies:
        return float(amount)

    return float(amount) / 100.0


def major_to_stripe_amount(amount, currency="inr"):
    """
    Convert database major-unit amount to Stripe
    smallest currency unit.

    Example:

        387036.46 INR
            ↓
        38703646
    """

    if amount is None:
        return None

    currency = normalize_status(currency or "inr")

    zero_decimal_currencies = {
        "bif",
        "clp",
        "djf",
        "gnf",
        "jpy",
        "kmf",
        "krw",
        "mga",
        "pyg",
        "rwf",
        "ugx",
        "vnd",
        "vuv",
        "xaf",
        "xof",
        "xpf",
    }

    if currency in zero_decimal_currencies:
        return int(round(float(amount)))

    return int(round(float(amount) * 100))


# =========================================================
# GET VERIFIED STRIPE PAYMENT INTENT
# =========================================================

def get_stripe_payment_intent(transaction_id):
    """
    Accept:

        pi_xxxxxxxxx

    OR:

        cs_xxxxxxxxx

    and return the REAL Stripe PaymentIntent ID.

    IMPORTANT:
    The returned ID must be verified from Stripe.
    """

    if not transaction_id:

        raise HTTPException(
            status_code=400,
            detail=(
                "Payment transaction ID is missing. "
                "The payment must be completed through Stripe "
                "before refund."
            )
        )

    transaction_id = str(transaction_id).strip()

    print(
        "Checking Stripe transaction:",
        transaction_id
    )

    # =====================================================
    # INVALID PLACEHOLDERS
    # =====================================================

    invalid_placeholders = {
        "",
        "none",
        "null",
        "undefined",
        "pi_actual_id",
        "actual_payment_intent",
        "your_payment_intent_id",
        "payment_intent_id",
    }

    if transaction_id.lower() in invalid_placeholders:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid Stripe PaymentIntent ID stored "
                "in database."
            )
        )

    # =====================================================
    # PAYMENT INTENT
    # =====================================================

    if transaction_id.startswith("pi_"):

        try:

            payment_intent = stripe.PaymentIntent.retrieve(
                transaction_id
            )

            payment_intent_id = stripe_id(
                payment_intent
            )

            if not payment_intent_id:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Stripe returned a PaymentIntent "
                        "without a valid ID."
                    )
                )

            if payment_intent_id != transaction_id:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Stripe PaymentIntent ID verification failed."
                    )
                )

            print(
                "Stripe PaymentIntent verified:",
                payment_intent_id
            )

            return payment_intent_id

        except HTTPException:
            raise

        except stripe.error.InvalidRequestError as e:

            print(
                "Stripe InvalidRequestError:",
                str(e)
            )

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Unable to retrieve Stripe PaymentIntent: "
                    f"{str(e)}"
                )
            )

        except stripe.error.AuthenticationError as e:

            print(
                "Stripe AuthenticationError:",
                str(e)
            )

            raise HTTPException(
                status_code=500,
                detail=(
                    "Stripe authentication failed. "
                    "Check STRIPE_SECRET_KEY."
                )
            )

        except stripe.error.StripeError as e:

            print(
                "Stripe PaymentIntent error:",
                str(e)
            )

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Unable to verify Stripe PaymentIntent: "
                    f"{str(e)}"
                )
            )

        except Exception as e:

            print(
                "Unexpected PaymentIntent error:",
                repr(e)
            )

            raise HTTPException(
                status_code=500,
                detail=(
                    "Unexpected error while verifying "
                    "Stripe PaymentIntent."
                )
            )

    # =====================================================
    # CHECKOUT SESSION
    # =====================================================

    if transaction_id.startswith("cs_"):

        try:

            session = stripe.checkout.Session.retrieve(
                transaction_id,
                expand=["payment_intent"]
            )

            payment_status = normalize_status(
                stripe_value(
                    session,
                    "payment_status"
                )
            )

            print(
                "Checkout Session Payment Status:",
                payment_status
            )

            if payment_status != "paid":

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Stripe Checkout Session is not paid. "
                        f"Payment status: {payment_status}"
                    )
                )

            payment_intent = stripe_value(
                session,
                "payment_intent"
            )

            payment_intent_id = stripe_id(
                payment_intent
            )

            if not payment_intent_id:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Checkout Session does not contain "
                        "a valid PaymentIntent."
                    )
                )

            if not str(payment_intent_id).startswith("pi_"):

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Checkout Session contains an invalid "
                        "PaymentIntent ID."
                    )
                )

            print(
                "Checkout Session converted to PaymentIntent:",
                payment_intent_id
            )

            return payment_intent_id

        except HTTPException:
            raise

        except stripe.error.InvalidRequestError as e:

            print(
                "Stripe Checkout Session InvalidRequestError:",
                str(e)
            )

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Unable to retrieve Stripe Checkout Session: "
                    f"{str(e)}"
                )
            )

        except stripe.error.AuthenticationError as e:

            print(
                "Stripe Checkout Session authentication error:",
                str(e)
            )

            raise HTTPException(
                status_code=500,
                detail=(
                    "Stripe authentication failed. "
                    "Check STRIPE_SECRET_KEY."
                )
            )

        except stripe.error.StripeError as e:

            print(
                "Stripe Checkout Session error:",
                str(e)
            )

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Unable to verify Stripe Checkout Session: "
                    f"{str(e)}"
                )
            )

        except Exception as e:

            print(
                "Unexpected Checkout Session error:",
                repr(e)
            )

            raise HTTPException(
                status_code=500,
                detail=(
                    "Unexpected error while verifying "
                    "Stripe Checkout Session."
                )
            )

    # =====================================================
    # UNKNOWN FORMAT
    # =====================================================

    raise HTTPException(
        status_code=400,
        detail=(
            "Invalid Stripe transaction ID. "
            "Expected pi_... or cs_..."
        )
    )


# =========================================================
# VERIFY STRIPE PAYMENT INTENT
# =========================================================

def retrieve_verified_payment_intent(payment_intent_id):
    """
    Retrieve and verify the PaymentIntent from Stripe.
    """

    if not payment_intent_id:

        raise HTTPException(
            status_code=400,
            detail="PaymentIntent ID is missing."
        )

    if not str(payment_intent_id).startswith("pi_"):

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid PaymentIntent ID. "
                "Expected pi_..."
            )
        )

    try:

        payment_intent = stripe.PaymentIntent.retrieve(
            payment_intent_id
        )

    except stripe.error.InvalidRequestError as e:

        print(
            "Stripe PaymentIntent does not exist:",
            str(e)
        )

        raise HTTPException(
            status_code=400,
            detail=(
                f"Unable to retrieve Stripe PaymentIntent: "
                f"{str(e)}"
            )
        )

    except stripe.error.AuthenticationError as e:

        print(
            "Stripe authentication error:",
            str(e)
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Stripe authentication failed. "
                "Check STRIPE_SECRET_KEY."
            )
        )

    except stripe.error.StripeError as e:

        print(
            "Stripe PaymentIntent error:",
            str(e)
        )

        raise HTTPException(
            status_code=400,
            detail=(
                f"Stripe PaymentIntent verification failed: "
                f"{str(e)}"
            )
        )

    except Exception as e:

        print(
            "Unexpected Stripe PaymentIntent error:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unexpected error while verifying "
                "Stripe PaymentIntent."
            )
        )

    verified_id = stripe_id(
        payment_intent
    )

    if verified_id != payment_intent_id:

        raise HTTPException(
            status_code=400,
            detail=(
                "Stripe PaymentIntent ID verification failed."
            )
        )

    stripe_status = normalize_status(
        stripe_value(
            payment_intent,
            "status"
        )
    )

    print(
        "Verified PaymentIntent ID:",
        verified_id
    )

    print(
        "Verified PaymentIntent Status:",
        stripe_status
    )

    if stripe_status != "succeeded":

        raise HTTPException(
            status_code=400,
            detail=(
                "Stripe PaymentIntent is not successfully "
                f"paid. Current status: {stripe_status}"
            )
        )

    return payment_intent


# =========================================================
# CREATE DATABASE NOTIFICATION
# =========================================================

def create_admin_notification(
    db: Session,
    user_id: int,
    notification_type: str,
    message: str
):
    """
    Create in-app notification.

    Notification failure must NOT break a completed
    payment/refund.
    """

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
            "Notification creation failed:",
            repr(e)
        )

        return None


# =========================================================
# SEND EMAIL
# =========================================================

def send_return_email(
    user_email: str,
    subject: str,
    message: str
):
    """
    Send email without breaking the main operation.
    """

    try:

        send_email(
            to_email=user_email,
            subject=subject,
            body=message
        )

        print(
            "Email sent successfully to:",
            user_email
        )

        return True

    except Exception as e:

        print(
            "Email sending failed:",
            repr(e)
        )

        return False


# =========================================================
# ADMIN USERS
# =========================================================

@router.get("/users")
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Get all users.
    """

    users = (
        db.query(User)
        .order_by(User.id.desc())
        .all()
    )

    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at,
        }
        for user in users
    ]


# =========================================================
# ADMIN ANALYTICS
# =========================================================

@router.get("/analytics")
def get_admin_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Basic admin analytics.
    """

    total_users = db.query(User).count()

    total_products = db.query(Product).count()

    total_orders = db.query(Order).count()

    total_returns = db.query(ReturnRequest).count()

    total_revenue = (
        db.query(func.sum(Payment.amount))
        .filter(
            normalize_status(Payment.status) == "paid"
        )
        .scalar()
        or 0
    )

    return {
        "total_users": total_users,
        "total_products": total_products,
        "total_orders": total_orders,
        "total_returns": total_returns,
        "total_revenue": float(total_revenue),
    }


# =========================================================
# GET ALL RETURN REQUESTS
# =========================================================

@router.get("/returns")
def get_all_returns(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Get all customer return requests.
    """

    returns = (
        db.query(ReturnRequest)
        .order_by(ReturnRequest.id.desc())
        .all()
    )

    response = []

    for return_request in returns:

        order = (
            db.query(Order)
            .filter(
                Order.id == return_request.order_id
            )
            .first()
        )

        payment = (
            db.query(Payment)
            .filter(
                Payment.order_id == return_request.order_id
            )
            .order_by(Payment.id.desc())
            .first()
        )

        response.append(
            {
                "id": return_request.id,
                "order_id": return_request.order_id,
                "user_id": return_request.user_id,
                "reason": return_request.reason,
                "comment": return_request.comment,
                "status": return_request.status,
                "created_at": return_request.created_at,

                "order_status": (
                    order.order_status
                    if order
                    else None
                ),

                "payment": {
                    "id": (
                        payment.id
                        if payment
                        else None
                    ),

                    "amount": (
                        payment.amount
                        if payment
                        else None
                    ),

                    "payment_method": (
                        payment.payment_method
                        if payment
                        else None
                    ),

                    "status": (
                        payment.status
                        if payment
                        else None
                    ),

                    "transaction_id": (
                        payment.transaction_id
                        if payment
                        else None
                    ),

                    "refund_id": (
                        payment.refund_id
                        if payment
                        else None
                    ),

                    "refund_amount": (
                        payment.refund_amount
                        if payment
                        else None
                    ),

                    "refunded_at": (
                        payment.refunded_at
                        if payment
                        else None
                    ),
                }
            }
        )

    return response


# =========================================================
# APPROVE RETURN
# =========================================================

@router.post("/returns/{return_id}/approve")
def approve_return(
    return_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Approve customer return.

    Workflow:

        pending
            ↓
        approved

    Also:

        Product stock increases
        Order status = Returned
    """

    return_request = (
        db.query(ReturnRequest)
        .filter(
            ReturnRequest.id == return_id
        )
        .with_for_update()
        .first()
    )

    if not return_request:

        raise HTTPException(
            status_code=404,
            detail="Return request not found."
        )

    return_status = normalize_status(
        return_request.status
    )

    if return_status != "pending":

        raise HTTPException(
            status_code=400,
            detail=(
                f"Return request is already "
                f"{return_request.status}."
            )
        )

    order = (
        db.query(Order)
        .filter(
            Order.id == return_request.order_id
        )
        .with_for_update()
        .first()
    )

    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order not found."
        )

    order_status = str(
        order.order_status or ""
    ).strip()

    allowed_statuses = {
        "Delivered",
        "Return Requested"
    }

    if order_status not in allowed_statuses:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Return cannot be approved because "
                f"order status is '{order.order_status}'."
            )
        )

    order_items = (
        db.query(OrderItem)
        .filter(
            OrderItem.order_id == order.id
        )
        .all()
    )

    if not order_items:

        raise HTTPException(
            status_code=400,
            detail="Order has no items."
        )

    # =====================================================
    # RESTORE INVENTORY
    # =====================================================

    for item in order_items:

        product = (
            db.query(Product)
            .filter(
                Product.id == item.product_id
            )
            .with_for_update()
            .first()
        )

        if product:

            quantity = item.quantity or 0

            product.stock = (
                (product.stock or 0)
                + quantity
            )

            print(
                f"Inventory restored: "
                f"Product {product.id}, "
                f"+{quantity}"
            )

    return_request.status = "approved"

    order.order_status = "Returned"

    try:

        db.commit()

        db.refresh(return_request)

        db.refresh(order)

    except Exception as e:

        db.rollback()

        print(
            "Return approval DB error:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to approve return."
        )

    # =====================================================
    # NOTIFICATION
    # =====================================================

    message = (
        f"Your return request #{return_request.id} "
        f"for order #{order.id} has been approved. "
        f"The order has been marked as Returned."
    )

    notification = create_admin_notification(
        db=db,
        user_id=return_request.user_id,
        notification_type="return_approved",
        message=message
    )

    # =====================================================
    # WEBSOCKET
    # =====================================================

    try:

        result = send_order_update(
            return_request.user_id,
            {
                "order_id": order.id,
                "order_status": "Returned",
                "return_status": "approved",
                "message": message,
            }
        )

        print(
            "Return approval order WebSocket:",
            result
        )

    except Exception as e:

        print(
            "Order WebSocket failed:",
            repr(e)
        )

    try:

        result = send_notification(
            return_request.user_id,
            {
                "type": "return_approved",
                "message": message,
            }
        )

        print(
            "Return approval notification WebSocket:",
            result
        )

    except Exception as e:

        print(
            "Notification WebSocket failed:",
            repr(e)
        )

    # =====================================================
    # EMAIL
    # =====================================================

    customer = (
        db.query(User)
        .filter(
            User.id == return_request.user_id
        )
        .first()
    )

    if customer and customer.email:

        send_return_email(
            user_email=customer.email,
            subject="Return Request Approved",
            message=message
        )

    return {
        "message": "Return approved successfully.",
        "return_id": return_request.id,
        "order_id": order.id,
        "return_status": return_request.status,
        "order_status": order.order_status,
        "notification_created": (
            notification is not None
        ),
    }


# =========================================================
# REJECT RETURN
# =========================================================

@router.post("/returns/{return_id}/reject")
def reject_return(
    return_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Reject pending return.

    Order remains Delivered.
    """

    return_request = (
        db.query(ReturnRequest)
        .filter(
            ReturnRequest.id == return_id
        )
        .with_for_update()
        .first()
    )

    if not return_request:

        raise HTTPException(
            status_code=404,
            detail="Return request not found."
        )

    if normalize_status(
        return_request.status
    ) != "pending":

        raise HTTPException(
            status_code=400,
            detail=(
                f"Return request is already "
                f"{return_request.status}."
            )
        )

    order = (
        db.query(Order)
        .filter(
            Order.id == return_request.order_id
        )
        .with_for_update()
        .first()
    )

    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order not found."
        )

    allowed_statuses = {
        "Delivered",
        "Return Requested"
    }

    if order.order_status not in allowed_statuses:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Return cannot be rejected because "
                f"order status is '{order.order_status}'."
            )
        )

    return_request.status = "rejected"

    order.order_status = "Delivered"

    try:

        db.commit()

        db.refresh(return_request)

        db.refresh(order)

    except Exception as e:

        db.rollback()

        print(
            "Return rejection DB error:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to reject return."
        )

    message = (
        f"Your return request #{return_request.id} "
        f"for order #{order.id} has been rejected."
    )

    notification = create_admin_notification(
        db=db,
        user_id=return_request.user_id,
        notification_type="return_rejected",
        message=message
    )

    # =====================================================
    # WEBSOCKET
    # =====================================================

    try:

        result = send_order_update(
            return_request.user_id,
            {
                "order_id": order.id,
                "order_status": "Delivered",
                "return_status": "rejected",
                "message": message,
            }
        )

        print(
            "Return rejection order WebSocket:",
            result
        )

    except Exception as e:

        print(
            "Order WebSocket failed:",
            repr(e)
        )

    try:

        result = send_notification(
            return_request.user_id,
            {
                "type": "return_rejected",
                "message": message,
            }
        )

        print(
            "Return rejection notification WebSocket:",
            result
        )

    except Exception as e:

        print(
            "Notification WebSocket failed:",
            repr(e)
        )

    # =====================================================
    # EMAIL
    # =====================================================

    customer = (
        db.query(User)
        .filter(
            User.id == return_request.user_id
        )
        .first()
    )

    if customer and customer.email:

        send_return_email(
            user_email=customer.email,
            subject="Return Request Rejected",
            message=message
        )

    return {
        "message": "Return rejected successfully.",
        "return_id": return_request.id,
        "order_id": order.id,
        "return_status": return_request.status,
        "order_status": order.order_status,
        "notification_created": (
            notification is not None
        ),
    }


# =========================================================
# REFUND RETURN
# =========================================================

@router.post("/returns/{return_id}/refund")
def refund_return(
    return_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Refund an approved return.

    Stripe:

        Payment.transaction_id
                |
                +--> pi_...
                |
                +--> cs_...
                         |
                         v
                   PaymentIntent
                         |
                         v
                    Stripe Refund
                         |
                         v
                 Database refunded
    """

    print("=" * 70)
    print("STARTING REFUND")
    print("RETURN ID:", return_id)
    print("=" * 70)

    # =====================================================
    # GET RETURN REQUEST WITH LOCK
    # =====================================================

    return_request = (
        db.query(ReturnRequest)
        .filter(
            ReturnRequest.id == return_id
        )
        .with_for_update()
        .first()
    )

    if not return_request:

        raise HTTPException(
            status_code=404,
            detail="Return request not found."
        )

    print(
        "Return Request:",
        return_request.id
    )

    print(
        "Return Status:",
        return_request.status
    )

    # =====================================================
    # RETURN MUST BE APPROVED
    # =====================================================

    current_return_status = normalize_status(
        return_request.status
    )

    if current_return_status != "approved":

        raise HTTPException(
            status_code=400,
            detail=(
                "Return must be approved before refund. "
                f"Current status: {return_request.status}"
            )
        )

    # =====================================================
    # GET ORDER
    # =====================================================

    order = (
        db.query(Order)
        .filter(
            Order.id == return_request.order_id
        )
        .with_for_update()
        .first()
    )

    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order not found."
        )

    print(
        "Order ID:",
        order.id
    )

    print(
        "Order Status:",
        order.order_status
    )

    # =====================================================
    # ORDER MUST BE RETURNED
    # =====================================================

    if str(order.order_status).strip().lower() != "returned":

        raise HTTPException(
            status_code=400,
            detail=(
                "Return approval must be completed before refund. "
                f"Current order status: {order.order_status}"
            )
        )

    # =====================================================
    # GET PAYMENT
    # =====================================================

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

    if not payment:

        raise HTTPException(
            status_code=404,
            detail="Payment not found for this order."
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
        "Payment Method:",
        payment.payment_method
    )

    print(
        "Database Transaction ID:",
        payment.transaction_id
    )

    print(
        "Database Payment Amount:",
        payment.amount
    )

    print(
        "Database Refund ID:",
        payment.refund_id
    )

    # =====================================================
    # ALREADY REFUNDED
    # =====================================================

    if normalize_status(
        payment.status
    ) == "refunded":

        print(
            "Payment already refunded."
        )

        return {
            "message": "Payment has already been refunded.",
            "return_id": return_request.id,
            "order_id": order.id,
            "payment_id": payment.id,
            "payment_status": payment.status,
            "return_status": return_request.status,
            "order_status": order.order_status,
            "transaction_id": payment.transaction_id,
            "refund_id": payment.refund_id,
            "refund_amount": payment.refund_amount,
            "refunded_at": payment.refunded_at,
        }

    # =====================================================
    # EXISTING REFUND ID
    # =====================================================

    if payment.refund_id:

        raise HTTPException(
            status_code=400,
            detail=(
                "A refund already exists for this payment. "
                f"Refund ID: {payment.refund_id}"
            )
        )

    # =====================================================
    # PAYMENT MUST BE PAID
    # =====================================================

    if normalize_status(
        payment.status
    ) != "paid":

        raise HTTPException(
            status_code=400,
            detail=(
                "Payment must have status 'Paid' before refund. "
                f"Current status: {payment.status}"
            )
        )

    # =====================================================
    # PAYMENT METHOD
    # =====================================================

    payment_method = (
        normalize_status(
            payment.payment_method
        )
        if payment.payment_method
        else ""
    )

    print(
        "Normalized Payment Method:",
        payment_method
    )

    # =====================================================
    # NON-STRIPE PAYMENT
    # =====================================================

    if payment_method != "stripe":

        print(
            "Non-Stripe payment detected."
        )

        payment.status = "Refunded"

        payment.refund_amount = (
            float(payment.amount)
            if payment.amount is not None
            else 0.0
        )

        payment.refunded_at = datetime.utcnow()

        return_request.status = "refunded"

        order.order_status = "Returned"

        try:

            db.commit()

            db.refresh(payment)

            db.refresh(return_request)

            db.refresh(order)

        except Exception as e:

            db.rollback()

            print(
                "Non-Stripe refund DB error:",
                repr(e)
            )

            raise HTTPException(
                status_code=500,
                detail="Failed to complete refund."
            )

        message = (
            f"Refund completed for order #{order.id}. "
            f"Refund amount: {payment.refund_amount}"
        )

        notification = create_admin_notification(
            db=db,
            user_id=return_request.user_id,
            notification_type="refund_completed",
            message=message
        )

        # =================================================
        # ORDER WEBSOCKET
        # =================================================

        try:

            result = send_order_update(
                return_request.user_id,
                {
                    "order_id": order.id,
                    "order_status": "Returned",
                    "payment_status": "Refunded",
                    "return_status": "refunded",
                    "message": message,
                }
            )

            print(
                "Refund order WebSocket:",
                result
            )

        except Exception as e:

            print(
                "Refund order WebSocket failed:",
                repr(e)
            )

        # =================================================
        # PAYMENT WEBSOCKET
        # =================================================

        try:

            result = send_payment_update(
                return_request.user_id,
                {
                    "order_id": order.id,
                    "payment_id": payment.id,
                    "payment_status": "Refunded",
                    "refund_amount": payment.refund_amount,
                }
            )

            print(
                "Refund payment WebSocket:",
                result
            )

        except Exception as e:

            print(
                "Refund payment WebSocket failed:",
                repr(e)
            )

        # =================================================
        # NOTIFICATION WEBSOCKET
        # =================================================

        try:

            result = send_notification(
                return_request.user_id,
                {
                    "type": "refund_completed",
                    "message": message,
                }
            )

            print(
                "Refund notification WebSocket:",
                result
            )

        except Exception as e:

            print(
                "Refund notification WebSocket failed:",
                repr(e)
            )

        # =================================================
        # EMAIL
        # =================================================

        customer = (
            db.query(User)
            .filter(
                User.id == return_request.user_id
            )
            .first()
        )

        email_sent = False

        if customer and customer.email:

            email_sent = send_return_email(
                user_email=customer.email,
                subject="Refund Completed",
                message=message
            )

        return {
            "message": "Refund completed successfully.",
            "return_id": return_request.id,
            "order_id": order.id,
            "payment_id": payment.id,
            "return_status": return_request.status,
            "payment_status": payment.status,
            "order_status": order.order_status,
            "refund_amount": payment.refund_amount,
            "notification_created": (
                notification is not None
            ),
            "email_sent": email_sent,
        }

    # =====================================================
    # STRIPE PAYMENT
    # =====================================================

    transaction_id = payment.transaction_id

    if not transaction_id:

        raise HTTPException(
            status_code=400,
            detail=(
                "Stripe payment does not have a transaction ID. "
                "The checkout.session.completed webhook must "
                "complete first."
            )
        )

    transaction_id = str(
        transaction_id
    ).strip()

    print(
        "Stripe Transaction ID from DB:",
        transaction_id
    )

    # =====================================================
    # GET PAYMENTINTENT ID
    # =====================================================

    payment_intent_id = get_stripe_payment_intent(
        transaction_id
    )

    print(
        "Verified PaymentIntent ID:",
        payment_intent_id
    )

    # =====================================================
    # RETRIEVE VERIFIED PAYMENTINTENT
    # =====================================================

    payment_intent = retrieve_verified_payment_intent(
        payment_intent_id
    )

    # =====================================================
    # STRIPE PAYMENTINTENT VALUES
    # =====================================================

    stripe_status = normalize_status(
        stripe_value(
            payment_intent,
            "status"
        )
    )

    stripe_amount = stripe_value(
        payment_intent,
        "amount"
    )

    stripe_currency = normalize_status(
        stripe_value(
            payment_intent,
            "currency",
            "inr"
        )
    )

    verified_id = stripe_id(
        payment_intent
    )

    print(
        "Stripe PaymentIntent ID:",
        verified_id
    )

    print(
        "Stripe PaymentIntent Status:",
        stripe_status
    )

    print(
        "Stripe PaymentIntent Amount:",
        stripe_amount
    )

    print(
        "Stripe PaymentIntent Currency:",
        stripe_currency
    )

    # =====================================================
    # PAYMENTINTENT STATUS
    # =====================================================

    if stripe_status != "succeeded":

        raise HTTPException(
            status_code=400,
            detail=(
                "Stripe PaymentIntent is not successfully paid. "
                f"Current Stripe status: {stripe_status}"
            )
        )

    # =====================================================
    # VERIFY PAYMENTINTENT ID
    # =====================================================

    if verified_id != payment_intent_id:

        raise HTTPException(
            status_code=400,
            detail=(
                "Stripe PaymentIntent ID verification failed."
            )
        )

    # =====================================================
    # VERIFY AMOUNT
    # =====================================================

    expected_stripe_amount = major_to_stripe_amount(
        payment.amount,
        stripe_currency
    )

    print(
        "Database Payment Amount:",
        payment.amount
    )

    print(
        "Expected Stripe Amount:",
        expected_stripe_amount
    )

    print(
        "Actual Stripe Amount:",
        stripe_amount
    )

    if (
        stripe_amount is None
        or expected_stripe_amount is None
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Unable to verify Stripe payment amount."
            )
        )

    if int(stripe_amount) != int(
        expected_stripe_amount
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Stripe payment amount does not match "
                "the database payment amount. "
                f"Stripe={stripe_amount}, "
                f"Database={expected_stripe_amount}, "
                f"Currency={stripe_currency}"
            )
        )

    print(
        "Stripe amount verification successful."
    )

    # =====================================================
    # UPDATE OLD CHECKOUT SESSION ID
    # =====================================================

    if payment.transaction_id != payment_intent_id:

        print(
            "Updating old transaction_id."
        )

        print(
            "Old transaction_id:",
            payment.transaction_id
        )

        print(
            "New transaction_id:",
            payment_intent_id
        )

        payment.transaction_id = payment_intent_id

        try:

            db.commit()

            db.refresh(payment)

        except Exception as e:

            db.rollback()

            print(
                "Failed to update transaction_id:",
                repr(e)
            )

            raise HTTPException(
                status_code=500,
                detail=(
                    "Failed to update payment transaction ID."
                )
            )

    # =====================================================
    # STRIPE REFUND
    # =====================================================

    print(
        "Creating Stripe refund..."
    )

    idempotency_key = (
        f"return_refund_{return_request.id}"
    )

    print(
        "Stripe Refund Idempotency Key:",
        idempotency_key
    )

    try:

        refund = stripe.Refund.create(
            payment_intent=payment_intent_id,
            idempotency_key=idempotency_key
        )

    except stripe.error.InvalidRequestError as e:

        print(
            "Stripe InvalidRequestError:",
            str(e)
        )

        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid Stripe refund request: {str(e)}"
            )
        )

    except stripe.error.AuthenticationError as e:

        print(
            "Stripe AuthenticationError:",
            str(e)
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Stripe authentication failed while "
                "creating refund."
            )
        )

    except stripe.error.StripeError as e:

        print(
            "Stripe refund error:",
            str(e)
        )

        raise HTTPException(
            status_code=400,
            detail=(
                f"Stripe refund failed: {str(e)}"
            )
        )

    except Exception as e:

        print(
            "Unexpected Stripe refund error:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unexpected error while creating "
                "Stripe refund."
            )
        )

    # =====================================================
    # READ REFUND SAFELY
    # =====================================================

    refund_id = stripe_id(
        refund
    )

    refund_status = normalize_status(
        stripe_value(
            refund,
            "status"
        )
    )

    refund_amount_minor = stripe_value(
        refund,
        "amount"
    )

    refund_currency = normalize_status(
        stripe_value(
            refund,
            "currency",
            stripe_currency
        )
    )

    print(
        "Stripe Refund ID:",
        refund_id
    )

    print(
        "Stripe Refund Status:",
        refund_status
    )

    print(
        "Stripe Refund Amount:",
        refund_amount_minor
    )

    print(
        "Stripe Refund Currency:",
        refund_currency
    )

    # =====================================================
    # VALIDATE REFUND ID
    # =====================================================

    if not refund_id:

        raise HTTPException(
            status_code=500,
            detail=(
                "Stripe returned a refund without "
                "a valid refund ID."
            )
        )

    # =====================================================
    # REFUND FAILED
    # =====================================================

    if refund_status == "failed":

        raise HTTPException(
            status_code=400,
            detail="Stripe refund failed."
        )

    # =====================================================
    # REFUND PENDING
    # =====================================================

    if refund_status == "pending":

        raise HTTPException(
            status_code=400,
            detail=(
                "Stripe refund is still pending. "
                "Payment was not marked as refunded yet."
            )
        )

    # =====================================================
    # REFUND MUST BE SUCCEEDED
    # =====================================================

    if refund_status != "succeeded":

        raise HTTPException(
            status_code=400,
            detail=(
                "Unexpected Stripe refund status: "
                f"{refund_status}"
            )
        )

    print(
        "Stripe refund succeeded."
    )

    # =====================================================
    # CONVERT REFUND AMOUNT
    # =====================================================

    refund_amount_major = stripe_amount_to_major(
        refund_amount_minor,
        refund_currency
    )

    print(
        "Refund Amount in Database Currency:",
        refund_amount_major
    )

    # =====================================================
    # VERIFY REFUND AMOUNT
    # =====================================================

    expected_refund_amount = float(
        payment.amount
        if payment.amount is not None
        else 0
    )

    if refund_amount_major is not None:

        # Small tolerance for floating point conversion.
        if abs(
            float(refund_amount_major)
            - expected_refund_amount
        ) > 0.01:

            print(
                "WARNING: Refund amount differs from "
                "database payment amount."
            )

            print(
                "Expected:",
                expected_refund_amount
            )

            print(
                "Actual:",
                refund_amount_major
            )

    # =====================================================
    # UPDATE DATABASE
    #
    # IMPORTANT:
    # Stripe refund has already succeeded here.
    # =====================================================

    payment.transaction_id = payment_intent_id

    payment.status = "Refunded"

    payment.refund_id = refund_id

    payment.refund_amount = refund_amount_major

    payment.refunded_at = datetime.utcnow()

    return_request.status = "refunded"

    # Order MUST remain Returned.

    order.order_status = "Returned"

    print(
        "Saving refund information to database..."
    )

    try:

        db.commit()

        db.refresh(payment)

        db.refresh(return_request)

        db.refresh(order)

    except Exception as e:

        db.rollback()

        print("=" * 70)
        print(
            "CRITICAL DATABASE ERROR AFTER STRIPE REFUND"
        )
        print(
            "Stripe Refund ID:",
            refund_id
        )
        print(
            "PaymentIntent ID:",
            payment_intent_id
        )
        print(
            "IMPORTANT: DO NOT create another manual refund."
        )
        print(
            "Retrying this endpoint uses the same "
            "Stripe idempotency key:"
        )
        print(
            idempotency_key
        )
        print(
            "Database error:",
            repr(e)
        )
        print("=" * 70)

        raise HTTPException(
            status_code=500,
            detail=(
                "Stripe refund succeeded, but saving "
                "refund information to the database failed. "
                f"Stripe Refund ID: {refund_id}"
            )
        )

    # =====================================================
    # SUCCESS LOG
    # =====================================================

    print(
        "PAYMENT DATABASE UPDATED"
    )

    print(
        "Payment Status:",
        payment.status
    )

    print(
        "Return Status:",
        return_request.status
    )

    print(
        "Order Status:",
        order.order_status
    )

    print(
        "Transaction ID:",
        payment.transaction_id
    )

    print(
        "Refund ID:",
        payment.refund_id
    )

    print(
        "Refund Amount:",
        payment.refund_amount
    )

    # =====================================================
    # CUSTOMER MESSAGE
    # =====================================================

    message = (
        f"Refund completed successfully for "
        f"order #{order.id}. "
        f"Refund amount: {payment.refund_amount}."
    )

    # =====================================================
    # DATABASE NOTIFICATION
    # =====================================================

    notification = create_admin_notification(
        db=db,
        user_id=return_request.user_id,
        notification_type="refund_completed",
        message=message
    )

    # =====================================================
    # ORDER WEBSOCKET
    # =====================================================

    try:

        result = send_order_update(
            return_request.user_id,
            {
                "order_id": order.id,
                "order_status": "Returned",
                "payment_status": "Refunded",
                "return_status": "refunded",
                "refund_id": payment.refund_id,
                "refund_amount": payment.refund_amount,
                "message": message,
            }
        )

        print(
            "Stripe order WebSocket result:",
            result
        )

    except Exception as e:

        print(
            "Stripe order WebSocket failed:",
            repr(e)
        )

    # =====================================================
    # PAYMENT WEBSOCKET
    # =====================================================

    try:

        result = send_payment_update(
            return_request.user_id,
            {
                "order_id": order.id,
                "payment_id": payment.id,
                "payment_status": "Refunded",
                "transaction_id": payment.transaction_id,
                "refund_id": payment.refund_id,
                "refund_amount": payment.refund_amount,
            }
        )

        print(
            "Stripe payment WebSocket result:",
            result
        )

    except Exception as e:

        print(
            "Stripe payment WebSocket failed:",
            repr(e)
        )

    # =====================================================
    # NOTIFICATION WEBSOCKET
    # =====================================================

    try:

        result = send_notification(
            return_request.user_id,
            {
                "type": "refund_completed",
                "message": message,
                "order_id": order.id,
                "refund_id": payment.refund_id,
                "refund_amount": payment.refund_amount,
            }
        )

        print(
            "Stripe notification WebSocket result:",
            result
        )

    except Exception as e:

        print(
            "Stripe notification WebSocket failed:",
            repr(e)
        )

    # =====================================================
    # EMAIL
    # =====================================================

    customer = (
        db.query(User)
        .filter(
            User.id == return_request.user_id
        )
        .first()
    )

    email_sent = False

    if customer and customer.email:

        email_sent = send_return_email(
            user_email=customer.email,
            subject="Refund Completed",
            message=message
        )

    # =====================================================
    # FINAL RESPONSE
    # =====================================================

    print("=" * 70)
    print(
        "STRIPE REFUND COMPLETED SUCCESSFULLY"
    )
    print(
        "Return ID:",
        return_request.id
    )
    print(
        "Order ID:",
        order.id
    )
    print(
        "Payment ID:",
        payment.id
    )
    print(
        "PaymentIntent:",
        payment.transaction_id
    )
    print(
        "Refund ID:",
        payment.refund_id
    )
    print(
        "Refund Amount:",
        payment.refund_amount
    )
    print(
        "Payment Status:",
        payment.status
    )
    print(
        "Return Status:",
        return_request.status
    )
    print(
        "Order Status:",
        order.order_status
    )
    print("=" * 70)

    return {
        "message": "Refund completed successfully.",

        "return_id": return_request.id,

        "order_id": order.id,

        "payment_id": payment.id,

        "payment_status": payment.status,

        "return_status": return_request.status,

        "order_status": order.order_status,

        "transaction_id": payment.transaction_id,

        "refund_id": payment.refund_id,

        "refund_amount": payment.refund_amount,

        "refunded_at": payment.refunded_at,

        "currency": refund_currency,

        "notification_created": (
            notification is not None
        ),

        "email_sent": email_sent,
    }