from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Import SQLAlchemy Base
from app.database import Base

# Import models so all tables are registered in Base.metadata
from app import models


# ---------------------------------------------------------
# Alembic Config
# ---------------------------------------------------------

config = context.config


# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# ---------------------------------------------------------
# SQLAlchemy Metadata
# ---------------------------------------------------------

target_metadata = Base.metadata


# ---------------------------------------------------------
# Only manage SQLAlchemy tables
# Do NOT manage Django tables
# ---------------------------------------------------------

def include_object(
    object,
    name,
    type_,
    reflected,
    compare_to
):
    """
    Tell Alembic which database objects it should manage.

    If a table exists in the database but is NOT part of
    SQLAlchemy Base.metadata, Alembic will ignore it.

    This prevents Alembic from trying to delete Django tables
    such as:

        auth_user
        auth_group
        auth_permission
        django_admin_log
        django_content_type
        django_migrations
        django_session
    """

    if type_ == "table" and reflected:
        return name in target_metadata.tables

    return True


# ---------------------------------------------------------
# Offline Migration
# ---------------------------------------------------------

def run_migrations_offline() -> None:

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
        include_object=include_object,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():

        context.run_migrations()


# ---------------------------------------------------------
# Online Migration
# ---------------------------------------------------------

def run_migrations_online() -> None:

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():

            context.run_migrations()


# ---------------------------------------------------------
# Run
# ---------------------------------------------------------

if context.is_offline_mode():

    run_migrations_offline()

else:

    run_migrations_online()