from pydantic import BaseModel
from pydantic import EmailStr


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


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    stock: int
    images: str


class CartCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int

