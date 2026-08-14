from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Cart, Product


router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
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
# ADD TO CART
# =========================================================

@router.post("/add")
def add_to_cart(
    user_id: int,
    product_id: int,
    quantity: int = Query(default=1, ge=1),
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # FIND PRODUCT
    # -----------------------------------------------------

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product Not Found"
        )

    # -----------------------------------------------------
    # CHECK STOCK
    # -----------------------------------------------------

    if product.stock < quantity:
        raise HTTPException(
            status_code=400,
            detail="Insufficient Stock"
        )

    # -----------------------------------------------------
    # FIND EXISTING CART ITEM
    # -----------------------------------------------------

    cart = db.query(Cart).filter(
        Cart.user_id == user_id,
        Cart.product_id == product_id
    ).first()

    # -----------------------------------------------------
    # UPDATE EXISTING CART ITEM
    # -----------------------------------------------------

    if cart:

        cart.quantity += quantity

    # -----------------------------------------------------
    # CREATE NEW CART ITEM
    # -----------------------------------------------------

    else:

        cart = Cart(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity
        )

        db.add(cart)

    # -----------------------------------------------------
    # REDUCE STOCK
    # -----------------------------------------------------

    product.stock -= quantity

    # -----------------------------------------------------
    # INCREASE POPULARITY
    # -----------------------------------------------------

    product.popularity += quantity

    db.commit()
    db.refresh(cart)

    return {
        "message": "Added To Cart",
        "cart_id": cart.id,
        "product_id": product_id,
        "quantity": cart.quantity,
        "remaining_stock": product.stock
    }


# =========================================================
# VIEW CART + TOTALS
# =========================================================

@router.get("/")
def view_cart(
    user_id: int,
    db: Session = Depends(get_db)
):

    items = db.query(Cart).filter(
        Cart.user_id == user_id
    ).all()

    result = []

    cart_total = 0

    # -----------------------------------------------------
    # CALCULATE ITEM TOTALS
    # -----------------------------------------------------

    for item in items:

        item_total = (
            item.product.price *
            item.quantity
        )

        cart_total += item_total

        result.append({
            "cart_id": item.id,
            "product_id": item.product.id,
            "product_name": item.product.name,
            "category": item.product.category,
            "price": item.product.price,
            "quantity": item.quantity,
            "item_total": round(item_total, 2)
        })

    # -----------------------------------------------------
    # TAX
    # -----------------------------------------------------

    tax = round(
        cart_total * 0.18,
        2
    )

    # -----------------------------------------------------
    # GRAND TOTAL
    # -----------------------------------------------------

    grand_total = round(
        cart_total + tax,
        2
    )

    return {
        "items": result,
        "cart_total": round(cart_total, 2),
        "tax": tax,
        "grand_total": grand_total
    }


# =========================================================
# UPDATE CART QUANTITY
# =========================================================

@router.put("/update/{cart_id}")
def update_cart(
    cart_id: int,
    quantity: int = Query(..., ge=1),
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # FIND CART
    # -----------------------------------------------------

    cart = db.query(Cart).filter(
        Cart.id == cart_id
    ).first()

    if not cart:
        raise HTTPException(
            status_code=404,
            detail="Cart Not Found"
        )

    # -----------------------------------------------------
    # FIND PRODUCT
    # -----------------------------------------------------

    product = db.query(Product).filter(
        Product.id == cart.product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product Not Found"
        )

    # -----------------------------------------------------
    # CALCULATE QUANTITY DIFFERENCE
    # -----------------------------------------------------

    old_quantity = cart.quantity

    difference = quantity - old_quantity

    # -----------------------------------------------------
    # INCREASING CART QUANTITY
    # -----------------------------------------------------

    if difference > 0:

        if product.stock < difference:

            raise HTTPException(
                status_code=400,
                detail="Insufficient Stock"
            )

        product.stock -= difference

    # -----------------------------------------------------
    # DECREASING CART QUANTITY
    # -----------------------------------------------------

    elif difference < 0:

        product.stock += abs(difference)

    # -----------------------------------------------------
    # UPDATE CART
    # -----------------------------------------------------

    cart.quantity = quantity

    db.commit()
    db.refresh(cart)

    return {
        "message": "Cart Updated Successfully",
        "cart_id": cart.id,
        "product_id": cart.product_id,
        "quantity": cart.quantity,
        "remaining_stock": product.stock
    }


# =========================================================
# REMOVE CART ITEM
# =========================================================

@router.delete("/remove/{cart_id}")
def remove_cart(
    cart_id: int,
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # FIND CART
    # -----------------------------------------------------

    cart = db.query(Cart).filter(
        Cart.id == cart_id
    ).first()

    if not cart:
        raise HTTPException(
            status_code=404,
            detail="Cart Not Found"
        )

    # -----------------------------------------------------
    # FIND PRODUCT
    # -----------------------------------------------------

    product = db.query(Product).filter(
        Product.id == cart.product_id
    ).first()

    # -----------------------------------------------------
    # RETURN RESERVED STOCK
    # -----------------------------------------------------

    if product:

        product.stock += cart.quantity

    # -----------------------------------------------------
    # DELETE CART ITEM
    # -----------------------------------------------------

    db.delete(cart)

    db.commit()

    return {
        "message": "Removed Successfully",
        "returned_stock": cart.quantity
    }