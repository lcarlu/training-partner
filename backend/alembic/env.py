from logging.config import fileConfig

from alembic.ddl.impl import DefaultImpl
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

from alembic import context
from app.core.config import get_settings
from app.core.db import APP_SCHEMA
from app.infrastructure.db import models  # noqa: F401  (registers tables on SQLModel.metadata)


class DuckDBImpl(DefaultImpl):
    """duckdb-engine doesn't ship an Alembic DDL impl; the Postgres-derived default works."""

    __dialect__ = "duckdb"


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", f"duckdb:///{get_settings().duckdb_path}")

target_metadata = SQLModel.metadata


def include_object(object, name, type_, reflected, compare_to):  # noqa: A002
    if type_ == "table":
        return getattr(object, "schema", None) == APP_SCHEMA
    return True


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
        version_table_schema=APP_SCHEMA,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        connection.exec_driver_sql(f"CREATE SCHEMA IF NOT EXISTS {APP_SCHEMA}")
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
            version_table_schema=APP_SCHEMA,
        )

        with context.begin_transaction():
            context.run_migrations()

        # duckdb-engine doesn't support switching isolation level to AUTOCOMMIT, and
        # Alembic's "non-transactional DDL" assumption otherwise leaves this connection's
        # implicit transaction uncommitted, silently rolled back on close.
        connection.commit()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
