"""sync database schema

Revision ID: 82f6cc428753
Revises: ae7fde1073f0
Create Date: 2026-08-26 13:39:07.947774

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision: str = "82f6cc428753"
down_revision: Union[str, Sequence[str], None] = "ae7fde1073f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""

    # =========================
    # CART
    # =========================

    op.alter_column(
        "cart",
        "user_id",
        existing_type=mysql.INTEGER(),
        nullable=False,
    )

    op.alter_column(
        "cart",
        "product_id",
        existing_type=mysql.INTEGER(),
        nullable=False,
    )

    op.alter_column(
        "cart",
        "quantity",
        existing_type=mysql.INTEGER(),
        nullable=False,
    )

    # ix_cart_id intentionally NOT created.
    # cart.id already has PRIMARY KEY.


    # =========================
    # NOTIFICATIONS
    # =========================

    op.alter_column(
        "notifications",
        "user_id",
        existing_type=mysql.INTEGER(),
        nullable=False,
    )

    op.alter_column(
        "notifications",
        "type",
        existing_type=mysql.VARCHAR(length=50),
        nullable=False,
    )

    op.alter_column(
        "notifications",
        "message",
        existing_type=mysql.VARCHAR(length=255),
        nullable=False,
    )

    op.alter_column(
        "notifications",
        "read_status",
        existing_type=mysql.TINYINT(display_width=1),
        nullable=False,
    )

    op.alter_column(
        "notifications",
        "timestamp",
        existing_type=mysql.DATETIME(),
        nullable=False,
    )

    # Create only if this index does not already exist.
    conn = op.get_bind()

    result = conn.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM information_schema.statistics
            WHERE table_schema = DATABASE()
            AND table_name = 'notifications'
            AND index_name = 'ix_notifications_user_id'
            """
        )
    )

    if result.scalar() == 0:
        op.create_index(
            "ix_notifications_user_id",
            "notifications",
            ["user_id"],
            unique=False,
        )


    # =========================
    # ORDER ITEMS
    # =========================

    result = conn.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM information_schema.statistics
            WHERE table_schema = DATABASE()
            AND table_name = 'order_items'
            AND index_name = 'ix_order_items_order_id'
            """
        )
    )

    if result.scalar() == 0:
        op.create_index(
            "ix_order_items_order_id",
            "order_items",
            ["order_id"],
            unique=False,
        )

    result = conn.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM information_schema.statistics
            WHERE table_schema = DATABASE()
            AND table_name = 'order_items'
            AND index_name = 'ix_order_items_product_id'
            """
        )
    )

    if result.scalar() == 0:
        op.create_index(
            "ix_order_items_product_id",
            "order_items",
            ["product_id"],
            unique=False,
        )


    # =========================
    # ORDERS
    # =========================

    op.alter_column(
        "orders",
        "user_id",
        existing_type=mysql.INTEGER(),
        nullable=False,
    )

    op.alter_column(
        "orders",
        "total_amount",
        existing_type=mysql.FLOAT(),
        nullable=False,
    )

    op.alter_column(
        "orders",
        "payment_status",
        existing_type=mysql.VARCHAR(length=50),
        server_default=None,
        type_=sa.String(length=30),
        existing_nullable=False,
    )

    op.alter_column(
        "orders",
        "order_status",
        existing_type=mysql.VARCHAR(length=50),
        server_default=None,
        type_=sa.String(length=30),
        existing_nullable=False,
    )

    op.alter_column(
        "orders",
        "created_at",
        existing_type=mysql.DATETIME(),
        server_default=None,
        existing_nullable=False,
    )

    # orders.id already has PRIMARY KEY.
    # Do not create ix_orders_id.


    # =========================
    # PAYMENTS
    # =========================

    op.alter_column(
        "payments",
        "payment_method",
        existing_type=mysql.VARCHAR(length=50),
        nullable=False,
    )

    op.alter_column(
        "payments",
        "status",
        existing_type=mysql.VARCHAR(length=30),
        nullable=False,
    )

    op.alter_column(
        "payments",
        "timestamp",
        existing_type=mysql.DATETIME(),
        nullable=False,
    )

    result = conn.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM information_schema.statistics
            WHERE table_schema = DATABASE()
            AND table_name = 'payments'
            AND index_name = 'ix_payments_order_id'
            """
        )
    )

    if result.scalar() == 0:
        op.create_index(
            "ix_payments_order_id",
            "payments",
            ["order_id"],
            unique=False,
        )

    result = conn.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM information_schema.statistics
            WHERE table_schema = DATABASE()
            AND table_name = 'payments'
            AND index_name = 'ix_payments_transaction_id'
            """
        )
    )

    if result.scalar() == 0:
        op.create_index(
            "ix_payments_transaction_id",
            "payments",
            ["transaction_id"],
            unique=False,
        )


    # =========================
    # PRODUCTS
    # =========================

    op.alter_column(
        "products",
        "name",
        existing_type=mysql.VARCHAR(length=200),
        type_=sa.String(length=255),
        nullable=False,
    )

    op.alter_column(
        "products",
        "description",
        existing_type=mysql.VARCHAR(length=500),
        type_=sa.Text(),
        existing_nullable=True,
    )

    op.alter_column(
        "products",
        "category",
        existing_type=mysql.VARCHAR(length=100),
        nullable=False,
    )

    op.alter_column(
        "products",
        "price",
        existing_type=mysql.FLOAT(),
        nullable=False,
    )

    op.alter_column(
        "products",
        "stock",
        existing_type=mysql.INTEGER(),
        nullable=False,
    )

    op.alter_column(
        "products",
        "images",
        existing_type=mysql.VARCHAR(length=500),
        type_=sa.Text(),
        existing_nullable=True,
    )

    op.alter_column(
        "products",
        "popularity",
        existing_type=mysql.INTEGER(),
        server_default=None,
        existing_nullable=False,
    )

    # products.id already has PRIMARY KEY.
    # Do not create ix_products_id.


    # =========================
    # USERS
    # =========================

    op.alter_column(
        "users",
        "name",
        existing_type=mysql.VARCHAR(length=100),
        nullable=False,
    )

    op.alter_column(
        "users",
        "email",
        existing_type=mysql.VARCHAR(length=100),
        nullable=False,
    )

    op.alter_column(
        "users",
        "password",
        existing_type=mysql.VARCHAR(length=255),
        nullable=False,
    )

    op.alter_column(
        "users",
        "role",
        existing_type=mysql.VARCHAR(length=20),
        nullable=False,
    )

    # Replace old email index only if it exists.
    result = conn.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM information_schema.statistics
            WHERE table_schema = DATABASE()
            AND table_name = 'users'
            AND index_name = 'email'
            """
        )
    )

    if result.scalar() > 0:
        op.drop_index("email", table_name="users")

    # Create ix_users_email only if it does not already exist.
    result = conn.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM information_schema.statistics
            WHERE table_schema = DATABASE()
            AND table_name = 'users'
            AND index_name = 'ix_users_email'
            """
        )
    )

    if result.scalar() == 0:
        op.create_index(
            "ix_users_email",
            "users",
            ["email"],
            unique=True,
        )

    # users.id already has PRIMARY KEY.
    # Do not create ix_users_id.


def downgrade() -> None:
    """Downgrade database schema."""

    # This migration is primarily a schema synchronization migration.
    # Keep downgrade minimal to avoid accidentally deleting existing
    # production/database indexes.

    pass