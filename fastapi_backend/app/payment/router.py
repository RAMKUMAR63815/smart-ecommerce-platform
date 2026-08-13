from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Order

router = APIRouter(
    prefix="/payment",
    tags=["Payment"]
)


# =========================
# DATABASE SESSION
# =========================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# =========================
# GET PAYMENT ORDER
# =========================

@router.get("/{order_id}")
def get_payment_order(
    order_id: int,
    db: Session = Depends(get_db)
):

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

    return {
        "id": order.id,
        "user_id": order.user_id,
        "total_amount": order.total_amount,
        "status": order.status
    }


# =========================
# COMPLETE PAYMENT
# =========================

@router.post("/{order_id}/pay")
def complete_payment(
    order_id: int,
    db: Session = Depends(get_db)
):

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

    # Prevent paying twice
    if order.status == "Paid":
        return {
            "message": "Order is already paid",
            "order": {
                "id": order.id,
                "user_id": order.user_id,
                "total_amount": order.total_amount,
                "status": order.status
            }
        }

    # Change status
    order.status = "Paid"

    db.commit()
    db.refresh(order)

    return {
        "message": "Payment successful",
        "order": {
            "id": order.id,
            "user_id": order.user_id,
            "total_amount": order.total_amount,
            "status": order.status
        }
    }