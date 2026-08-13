from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Cart, Product


router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
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
# ADD TO CART
# =========================

@router.post("/add")
def add_to_cart(
    user_id: int,
    product_id: int,
    quantity: int = 1,
    db: Session = Depends(get_db)
):

    # Find product
    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product Not Found"
        )

    # Check quantity
    if quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0"
        )

    # Check stock
    if product.stock < quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Only {product.stock} items available"
        )

    # Check if product already exists in cart
    cart = (
        db.query(Cart)
        .filter(
            Cart.user_id == user_id,
            Cart.product_id == product_id
        )
        .first()
    )

    if cart:

        # Increase cart quantity
        cart.quantity += quantity

    else:

        # Create new cart item
        cart = Cart(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity
        )

        db.add(cart)

    # Reduce product stock
    product.stock -= quantity

    db.commit()

    db.refresh(cart)
    db.refresh(product)

    return {
        "message": "Added To Cart Successfully",

        "cart": {
            "id": cart.id,
            "user_id": cart.user_id,
            "product_id": cart.product_id,
            "quantity": cart.quantity,
            "product_name": product.name,
            "price": product.price,
            "total": product.price * cart.quantity
        },

        "remaining_stock": product.stock
    }


# =========================
# VIEW CART
# =========================

@router.get("/")
def view_cart(
    user_id: int,
    db: Session = Depends(get_db)
):

    cart_items = (
        db.query(Cart, Product)
        .join(
            Product,
            Cart.product_id == Product.id
        )
        .filter(
            Cart.user_id == user_id
        )
        .all()
    )

    result = []

    for cart, product in cart_items:

        result.append({
            "id": cart.id,
            "user_id": cart.user_id,
            "product_id": cart.product_id,
            "quantity": cart.quantity,

            "product_name": product.name,
            "description": product.description,
            "price": product.price,
            "image": product.images,

            "total": product.price * cart.quantity,

            "stock": product.stock
        })

    return {
        "count": len(result),
        "cart": result
    }


# =========================
# UPDATE QUANTITY
# =========================

@router.put("/update/{cart_id}")
def update_cart(
    cart_id: int,
    quantity: int,
    db: Session = Depends(get_db)
):

    # Find cart
    cart = (
        db.query(Cart)
        .filter(Cart.id == cart_id)
        .first()
    )

    if not cart:
        raise HTTPException(
            status_code=404,
            detail="Cart Item Not Found"
        )

    # Quantity must be at least 1
    if quantity < 1:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be at least 1"
        )

    # Find product
    product = (
        db.query(Product)
        .filter(Product.id == cart.product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product Not Found"
        )

    # Calculate quantity difference
    difference = quantity - cart.quantity

    # Example:
    #
    # Old cart quantity = 1
    # New quantity = 2
    #
    # difference = 2 - 1 = 1
    #
    # Need to remove 1 more item from stock.

    if difference > 0:

        # Check available stock
        if product.stock < difference:

            raise HTTPException(
                status_code=400,
                detail=f"Only {product.stock} more items available"
            )

        # Reduce stock
        product.stock -= difference

    elif difference < 0:

        # Customer decreased quantity
        #
        # Example:
        # Old quantity = 3
        # New quantity = 2
        #
        # Return 1 item to stock.

        product.stock += abs(difference)

    # Update cart quantity
    cart.quantity = quantity

    db.commit()

    db.refresh(cart)
    db.refresh(product)

    return {
        "message": "Cart Updated",

        "cart_id": cart.id,

        "quantity": cart.quantity,

        "remaining_stock": product.stock
    }


# =========================
# REMOVE FROM CART
# =========================

@router.delete("/remove/{cart_id}")
def remove_from_cart(
    cart_id: int,
    db: Session = Depends(get_db)
):

    # Find cart item
    cart = (
        db.query(Cart)
        .filter(Cart.id == cart_id)
        .first()
    )

    if not cart:
        raise HTTPException(
            status_code=404,
            detail="Cart Item Not Found"
        )

    # Find product
    product = (
        db.query(Product)
        .filter(Product.id == cart.product_id)
        .first()
    )

    if product:

        # Return cart quantity back to stock
        product.stock += cart.quantity

    # Delete cart item
    db.delete(cart)

    db.commit()

    return {
        "message": "Removed From Cart"
    }