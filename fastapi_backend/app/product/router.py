from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Product
from app.schemas import ProductCreate
from app.dependencies import require_role


router = APIRouter(
    prefix="/products",
    tags=["Products"]
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
# CREATE PRODUCT
# =========================================================

@router.post("/", status_code=201)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):

    new_product = Product(
        name=product.name,
        description=product.description,
        category=product.category,
        price=product.price,
        stock=product.stock,
        images=product.images,
        popularity=0
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {
        "message": "Product Created Successfully",
        "product": new_product
    }


# =========================================================
# GET ALL PRODUCTS + FILTERS
# =========================================================

@router.get("/")
def get_products(
    category: str | None = Query(default=None),
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    min_popularity: int | None = Query(default=None, ge=0),
    in_stock: bool | None = Query(default=None),

    db: Session = Depends(get_db)
):

    query = db.query(Product)

    # -----------------------------------------------------
    # CATEGORY FILTER
    # -----------------------------------------------------

    if category:
        query = query.filter(
            Product.category.ilike(category)
        )

    # -----------------------------------------------------
    # MINIMUM PRICE
    # -----------------------------------------------------

    if min_price is not None:
        query = query.filter(
            Product.price >= min_price
        )

    # -----------------------------------------------------
    # MAXIMUM PRICE
    # -----------------------------------------------------

    if max_price is not None:
        query = query.filter(
            Product.price <= max_price
        )

    # -----------------------------------------------------
    # POPULARITY FILTER
    # -----------------------------------------------------

    if min_popularity is not None:
        query = query.filter(
            Product.popularity >= min_popularity
        )

    # -----------------------------------------------------
    # STOCK FILTER
    # -----------------------------------------------------

    if in_stock is True:
        query = query.filter(
            Product.stock > 0
        )

    elif in_stock is False:
        query = query.filter(
            Product.stock == 0
        )

    # -----------------------------------------------------
    # POPULAR PRODUCTS FIRST
    # -----------------------------------------------------

    query = query.order_by(
        Product.popularity.desc()
    )

    products = query.all()

    return products


# =========================================================
# GET PRODUCT BY ID
# =========================================================

@router.get("/{product_id}")
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product Not Found"
        )

    return product


# =========================================================
# GET PRODUCTS BY CATEGORY
# =========================================================

@router.get("/category/{category}")
def get_products_by_category(
    category: str,
    db: Session = Depends(get_db)
):

    products = db.query(Product).filter(
        Product.category.ilike(category)
    ).order_by(
        Product.popularity.desc()
    ).all()

    return products


# =========================================================
# UPDATE PRODUCT
# =========================================================

@router.put("/{product_id}")
def update_product(
    product_id: int,
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product Not Found"
        )

    product.name = product_data.name
    product.description = product_data.description
    product.category = product_data.category
    product.price = product_data.price
    product.stock = product_data.stock
    product.images = product_data.images

    db.commit()
    db.refresh(product)

    return {
        "message": "Product Updated Successfully",
        "product": product
    }


# =========================================================
# DELETE PRODUCT
# =========================================================

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product Not Found"
        )

    db.delete(product)
    db.commit()

    return {
        "message": "Product Deleted Successfully"
    }