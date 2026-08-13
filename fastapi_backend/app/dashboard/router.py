from fastapi import APIRouter
from app.database import SessionLocal
from app.models import User, Product, Cart, Order

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

@router.get("/")
def dashboard():

    db = SessionLocal()

    return {
        "total_users": db.query(User).count(),
        "total_products": db.query(Product).count(),
        "total_cart_items": db.query(Cart).count(),
        "total_orders": db.query(Order).count()
    }