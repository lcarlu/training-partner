from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, text
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import get_settings

APP_SCHEMA = "app"


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()
    engine = create_engine(f"duckdb:///{settings.duckdb_path}")
    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {APP_SCHEMA}"))
    return engine


def init_db() -> None:
    """Create app-owned tables directly (used by tests / first-run fallback).

    In normal operation, table creation/evolution goes through Alembic migrations.
    """
    from app.infrastructure.db import models  # noqa: F401  (ensure tables are registered)

    SQLModel.metadata.create_all(get_engine())


def get_session() -> Generator[Session]:
    with Session(get_engine()) as session:
        yield session
