from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    Text,
    DateTime,
    Boolean
)

from sqlalchemy.orm import relationship

from .database import Base


# =========================================================
# USER MODEL
# =========================================================

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(100),
        unique=True,
        index=True,
        nullable=False
    )

    password = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(20),
        default="customer",
        nullable=False
    )

    # Relationships

    carts = relationship(
        "Cart",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    orders = relationship(
        "Order",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan"
    )


# =========================================================
# PRODUCT MODEL
# =========================================================

class Product(Base):

    __tablename__ = "products"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(255),
        nullable=False
    )

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

    # Relationship

    carts = relationship(
        "Cart",
        back_populates="product",
        cascade="all, delete-orphan"
    )


# =========================================================
# CART MODEL
# =========================================================

class Cart(Base):

    __tablename__ = "cart"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )

    quantity = Column(
        Integer,
        default=1,
        nullable=False
    )

    # Relationships

    user = relationship(
        "User",
        back_populates="carts"
    )

    product = relationship(
        "Product",
        back_populates="carts"
    )


# =========================================================
# ORDER MODEL
# =========================================================

class Order(Base):

    __tablename__ = "orders"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    total_amount = Column(
        Float,
        nullable=False
    )

    # -----------------------------------------------------
    # PAYMENT STATUS
    #
    # pending
    # paid
    # failed
    # cancelled
    # -----------------------------------------------------

    payment_status = Column(
        String(30),
        default="pending",
        nullable=False
    )

    # -----------------------------------------------------
    # ORDER STATUS
    #
    # pending
    # confirmed
    # processing
    # shipped
    # delivered
    # cancelled
    # -----------------------------------------------------

    order_status = Column(
        String(30),
        default="pending",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships

    user = relationship(
        "User",
        back_populates="orders"
    )

    payments = relationship(
        "Payment",
        back_populates="order",
        cascade="all, delete-orphan"
    )


# =========================================================
# PAYMENT MODEL
# =========================================================

class Payment(Base):

    __tablename__ = "payments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    order_id = Column(
        Integer,
        ForeignKey("orders.id"),
        nullable=False
    )

    amount = Column(
        Float,
        nullable=False
    )

    # stripe / cod / upi / card

    payment_method = Column(
        String(50),
        default="stripe",
        nullable=False
    )

    # Stripe PaymentIntent ID / Checkout Session ID

    transaction_id = Column(
        String(255),
        nullable=True,
        index=True
    )

    # pending / paid / failed / cancelled

    status = Column(
        String(30),
        default="pending",
        nullable=False
    )

    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationship

    order = relationship(
        "Order",
        back_populates="payments"
    )


# =========================================================
# NOTIFICATION MODEL
# =========================================================

class Notification(Base):

    __tablename__ = "notifications"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    type = Column(
        String(50),
        nullable=False
    )

    message = Column(
        String(255),
        nullable=False
    )

    read_status = Column(
        Boolean,
        default=False,
        nullable=False
    )

    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationship

    user = relationship(
        "User",
        back_populates="notifications"
    )