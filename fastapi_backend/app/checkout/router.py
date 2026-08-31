import stripe

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Cart, Product, Order, Payment
from app.core.config import STRIPE_SECRET_KEY


# =========================================================
# STRIPE CONFIG
# =========================================================

stripe.api_key = STRIPE_SECRET_KEY


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/checkout",
    tags=["Checkout"]
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
# CHECKOUT
# =========================================================

@router.post("/")
def checkout(
    user_id: int,
    db: Session = Depends(get_db)
):

    # =====================================================
    # 1. GET CART
    # =====================================================

    cart_items = (
        db.query(Cart)
        .filter(
            Cart.user_id == user_id
        )
        .all()
    )

    if not cart_items:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty"
        )

    # =====================================================
    # 2. CALCULATE CART TOTAL
    # =====================================================

    cart_total = 0.0

    for item in cart_items:

        product = (
            db.query(Product)
            .filter(
                Product.id == item.product_id
            )
            .first()
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Product {item.product_id} "
                    "not found"
                )
            )

        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Insufficient stock for "
                    f"{product.name}"
                )
            )

        cart_total += (
            float(product.price)
            * item.quantity
        )

    # =====================================================
    # 3. TAX
    # =====================================================

    tax = round(
        cart_total * 0.18,
        2
    )

    # =====================================================
    # 4. GRAND TOTAL
    # =====================================================

    total_amount = round(
        cart_total + tax,
        2
    )

    print("----------------------------------------")
    print("CHECKOUT")
    print("User ID:", user_id)
    print("Cart Total:", cart_total)
    print("Tax:", tax)
    print("Grand Total:", total_amount)
    print("----------------------------------------")

    # =====================================================
    # 5. CREATE ORDER
    # =====================================================

    order = Order(
        user_id=user_id,
        total_amount=total_amount,
        payment_status="pending",
        order_status="pending"
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    print(
        "ORDER CREATED:",
        order.id
    )

    # =====================================================
    # 6. CREATE PAYMENT
    # =====================================================

    payment = Payment(
        order_id=order.id,
        amount=total_amount,
        payment_method="stripe",
        status="pending"
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    print(
        "PAYMENT CREATED:",
        payment.id
    )

    # =====================================================
    # 7. CONVERT INR TO PAISE
    # =====================================================

    stripe_amount = int(
        round(total_amount * 100)
    )

    # =====================================================
    # 8. CREATE STRIPE CHECKOUT SESSION
    # =====================================================

    try:

        session = stripe.checkout.Session.create(

            mode="payment",

            line_items=[
                {
                    "price_data": {

                        "currency": "inr",

                        "product_data": {"name": (f"Order #{order.id}") },

                        "unit_amount": stripe_amount
                    },

                    "quantity": 1
                }
            ],

            metadata={
                "order_id": str(order.id),
                "payment_id": str(payment.id),
                "user_id": str(user_id)
            },

            success_url=(
                "http://localhost:5173/"
                "payment-success"
                "?session_id={CHECKOUT_SESSION_ID}"
            ),

            cancel_url=(
                "http://localhost:5173/"
                "payment-cancelled"
            )
        )

    except stripe.StripeError as e:

        print(
            "STRIPE ERROR:",
            repr(e)
        )

        db.delete(payment)
        db.delete(order)
        db.commit()

        raise HTTPException(
            status_code=500,
            detail=f"Stripe error: {str(e)}"
        )

    # =====================================================
    # 9. SAVE STRIPE SESSION ID
    # =====================================================

    payment.transaction_id = session.id

    db.commit()
    db.refresh(payment)

    print(
        "STRIPE SESSION:",
        session.id
    )

    # =====================================================
    # 10. RETURN CHECKOUT INFORMATION
    # =====================================================

    return {
        "message": "Checkout created successfully",

        "order_id": order.id,

        "payment_id": payment.id,

        "cart_total": round(
            cart_total,
            2
        ),

        "tax": tax,

        "amount": total_amount,

        "currency": "INR",

        "checkout_session_id": session.id,

        "checkout_url": session.url
    }