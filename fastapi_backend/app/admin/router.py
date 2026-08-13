from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import User, Product, Order
from ..dependencies import require_role


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


# =========================================================
# ADMIN - USERS
# =========================================================

@router.get("/users")
def get_users(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):
    users = db.query(User).all()

    return users


# =========================================================
# ADMIN - ANALYTICS
# =========================================================

@router.get("/analytics")
def get_analytics(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):
    # Total Users
    total_users = db.query(
        func.count(User.id)
    ).scalar() or 0

    # Total Products
    total_products = db.query(
        func.count(Product.id)
    ).scalar() or 0

    # Total Orders
    total_orders = db.query(
        func.count(Order.id)
    ).scalar() or 0

    # Revenue
    revenue = db.query(
        func.sum(Order.total_amount)
    ).scalar() or 0

    return {
        "total_users": total_users,
        "total_products": total_products,
        "total_orders": total_orders,
        "revenue": float(revenue)
    }