from pydantic import BaseModel, EmailStr, Field
from typing import Optional


# =========================================================
# USER SCHEMAS
# =========================================================

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# =========================================================
# PRODUCT SCHEMAS
# =========================================================

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float = Field(..., gt=0)
    category: str
    stock: int = Field(..., ge=0)
    images: str


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category: str
    stock: int
    images: str
    popularity: int

    class Config:
        from_attributes = True


# =========================================================
# CART SCHEMAS
# =========================================================

class CartCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int = Field(default=1, ge=1)


class CartUpdate(BaseModel):
    quantity: int = Field(..., ge=1)


class CartItemResponse(BaseModel):
    cart_id: int
    product_id: int
    product_name: str
    category: str
    price: float
    quantity: int
    item_total: float


class CartResponse(BaseModel):
    items: list[CartItemResponse]
    cart_total: float
    tax: float
    grand_total: float

class CheckoutRequest(BaseModel):

    user_id: int