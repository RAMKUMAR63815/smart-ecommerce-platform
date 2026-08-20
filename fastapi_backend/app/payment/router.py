from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Order, Payment


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

    # =====================================================
    # FIND ORDER
    # =====================================================

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

    # =====================================================
    # FIND PAYMENT
    # =====================================================

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

    # =====================================================
    # RESPONSE
    # =====================================================

    return {

        "order": {

            "id": order.id,

            "user_id": order.user_id,

            "total_amount": order.total_amount,

            "payment_status": (
                order.payment_status
            ),

            "order_status": (
                order.order_status
            ),

            # Frontend compatibility
            "status": (
                order.order_status
            ),

            "created_at": (
                order.created_at
            )
        },

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

            "transaction_id": (
                payment.transaction_id
                if payment
                else None
            ),

            "status": (
                payment.status
                if payment
                else None
            ),

            "timestamp": (
                payment.timestamp
                if payment
                else None
            )
        }
    }