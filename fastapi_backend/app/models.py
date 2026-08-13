from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float

from .database import Base


# =========================
# USER MODEL
# =========================

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=True
    )

    email = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    password = Column(
        String(255),
        nullable=True
    )

    role = Column(
        String(20),
        default="customer",
        nullable=False
    )


# =========================
# PRODUCT MODEL
# =========================

class Product(Base):

    __tablename__ = "products"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(200),
        nullable=True
    )

    description = Column(
        String(500),
        nullable=True
    )

    price = Column(
        Float,
        nullable=True
    )

    stock = Column(
        Integer,
        nullable=True
    )

    images = Column(
        String(500),
        nullable=True
    )


# =========================
# CART MODEL
# =========================

class Cart(Base):

    __tablename__ = "cart"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        nullable=False
    )

    product_id = Column(
        Integer,
        nullable=False
    )

    quantity = Column(
        Integer,
        nullable=False,
        default=1
    )


# =========================
# ORDER MODEL
# =========================

class Order(Base):

    __tablename__ = "orders"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        nullable=False
    )

    total_amount = Column(
        Float,
        nullable=True
    )

    status = Column(
        String(50),
        default="Pending",
        nullable=False
    )