from fastapi import APIRouter
from app.database import SessionLocal
from app.models import User, Product, Order

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

@router.get("/")
def analytics():

    db = SessionLocal()

    total_users = db.query(User).count()
    total_products = db.query(Product).count()
    total_orders = db.query(Order).count()
    
    revenue = 0

    orders = db.query(Order).all()

    for order in orders:
        revenue += order.total_amount

    return {
        "total_users": total_users,
        "total_products": total_products,
        "total_orders": total_orders,
        "total_revenue": revenue
    }