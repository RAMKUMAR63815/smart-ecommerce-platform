from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship

from .database import Base


# =========================
# USER MODEL
# =========================

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    password = Column(String(255))
    role = Column(String(20), default="customer")

    carts = relationship("Cart", back_populates="user")
    orders = relationship("Order", back_populates="user")


# =========================
# PRODUCT MODEL
# =========================
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False)

    description = Column(
        Text,
        nullable=True
    )

    category = Column(
        String(100),
        nullable=False
    )

    price = Column(
        Float,
        nullable=False
    )

    stock = Column(
        Integer,
        nullable=False,
        default=0
    )

    images = Column(
        Text,
        nullable=True
    )

    popularity = Column(
        Integer,
        nullable=False,
        default=0
    )

    carts = relationship(
        "Cart",
        back_populates="product"
    )


# =========================
# CART MODEL
# =========================

class Cart(Base):

    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))

    quantity = Column(Integer, default=1)

    user = relationship("User", back_populates="carts")
    product = relationship("Product", back_populates="carts")


# =========================
# ORDER MODEL
# =========================

class Order(Base):

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    total_amount = Column(Float)

    status = Column(String(50), default="Pending")

    user = relationship("User", back_populates="orders")