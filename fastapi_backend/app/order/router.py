from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Order, Cart, Product


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
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
# CREATE ORDER FROM CART
# =========================================================

@router.post("/create")
def create_order(
    user_id: int,
    db: Session = Depends(get_db)
):

    cart_items = (
        db.query(Cart)
        .filter(Cart.user_id == user_id)
        .all()
    )

    if not cart_items:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty"
        )

    total_amount = 0

    # Calculate total
    for item in cart_items:

        product = (
            db.query(Product)
            .filter(Product.id == item.product_id)
            .first()
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product {item.product_id} not found"
            )

        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for product {product.name}"
            )

        total_amount += product.price * item.quantity

    # =====================================================
    # CREATE ORDER
    # =====================================================

    order = Order(
        user_id=user_id,
        total_amount=total_amount,
        payment_status="Pending",
        order_status="Pending"
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    # =====================================================
    # REDUCE PRODUCT STOCK
    # =====================================================

    for item in cart_items:

        product = (
            db.query(Product)
            .filter(Product.id == item.product_id)
            .first()
        )

        product.stock -= item.quantity

    # =====================================================
    # CLEAR CART
    # =====================================================

    for item in cart_items:
        db.delete(item)

    db.commit()
    db.refresh(order)

    return {
        "message": "Order created successfully",
        "order": {
            "id": order.id,
            "user_id": order.user_id,
            "total_amount": order.total_amount,
            "payment_status": order.payment_status,
            "order_status": order.order_status,
            "status": order.order_status,
            "created_at": order.created_at
        }
    }


# =========================================================
# GET USER ORDERS
# =========================================================

@router.get("/")
def get_orders(
    user_id: int,
    db: Session = Depends(get_db)
):

    orders = (
        db.query(Order)
        .filter(Order.user_id == user_id)
        .order_by(Order.id.desc())
        .all()
    )

    result = []

    for order in orders:

        result.append({
            "id": order.id,
            "user_id": order.user_id,
            "total_amount": order.total_amount,

            # Payment status
            "payment_status": order.payment_status,

            # Order status
            "order_status": order.order_status,

            # Frontend compatibility
            "status": order.order_status,

            "created_at": order.created_at
        })

    return result


# =========================================================
# GET SINGLE ORDER
# =========================================================

@router.get("/{order_id}")
def get_order(
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
        "payment_status": order.payment_status,
        "order_status": order.order_status,

        # Frontend compatibility
        "status": order.order_status,

        "created_at": order.created_at
    }


# =========================================================
# PAYMENT SUCCESS
# =========================================================

@router.put("/{order_id}/pay")
def payment_success(
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

    # Already paid
    if order.payment_status == "Paid":

        return {
            "message": "Order already paid",
            "order": {
                "id": order.id,
                "user_id": order.user_id,
                "total_amount": order.total_amount,
                "payment_status": order.payment_status,
                "order_status": order.order_status,
                "status": order.order_status,
                "created_at": order.created_at
            }
        }

    # Update payment
    order.payment_status = "Paid"

    # Update order status
    order.order_status = "Confirmed"

    db.commit()
    db.refresh(order)

    return {
        "message": "Payment successful",
        "order": {
            "id": order.id,
            "user_id": order.user_id,
            "total_amount": order.total_amount,
            "payment_status": order.payment_status,
            "order_status": order.order_status,
            "status": order.order_status,
            "created_at": order.created_at
        }
    }