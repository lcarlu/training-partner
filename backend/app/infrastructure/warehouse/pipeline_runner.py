"""Orchestrates the sync: dlt extract (Garmin -> Postgres `raw`) then dbt transform
(`raw` -> `staging` -> `marts`), both in-process (no separate CLI subprocess).
"""

import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy.exc import ProgrammingError
from sqlmodel import Session, text

from app.core.db import get_engine
from app.infrastructure.db.repositories import SqlSyncLogRepository

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DATA_DIR = PROJECT_ROOT / "data"
DLT_DIR = DATA_DIR / "dlt"
DBT_DIR = DATA_DIR / "dbt"

_MART_TABLES = (
    "fct_activities",
    "fct_daily_wellness",
    "agg_weekly_volume_by_sport",
    "agg_training_load",
)


async def run_sync() -> dict[str, Any]:
    import asyncio

    return await asyncio.to_thread(_run_sync_blocking)


def _run_sync_blocking() -> dict[str, Any]:
    started_at = datetime.now(UTC)

    _run_dlt_extract()
    _run_dbt_transform()
    counts = _count_mart_rows()
    finished_at = datetime.now(UTC)

    with Session(get_engine()) as session:
        SqlSyncLogRepository(session).record(started_at, finished_at, counts)

    return {"started_at": started_at, "finished_at": finished_at, "counts": counts}


def _run_dlt_extract() -> None:
    if str(DLT_DIR) not in sys.path:
        sys.path.insert(0, str(DLT_DIR))
    # unresolved at static-analysis time: `garmin_pipeline` only exists on sys.path above.
    from garmin_pipeline import run_pipeline  # type: ignore[import-not-found]  # ty: ignore[unresolved-import]  # noqa: I001

    run_pipeline()


def _run_dbt_transform() -> None:
    import os

    from dbt.cli.main import dbtRunner

    from app.core.config import get_settings

    # profiles.yml reads these via env_var(); pydantic-settings loads backend/.env into
    # Settings without touching os.environ, so export them explicitly before invoking dbt.
    settings = get_settings()
    os.environ["POSTGRES_HOST"] = settings.postgres_host
    os.environ["POSTGRES_PORT"] = str(settings.postgres_port)
    os.environ["POSTGRES_USER"] = settings.postgres_user
    os.environ["POSTGRES_PASSWORD"] = settings.postgres_password
    os.environ["POSTGRES_DB"] = settings.postgres_db

    runner = dbtRunner()
    common_args = ["--project-dir", str(DBT_DIR), "--profiles-dir", str(DBT_DIR)]

    run_result = runner.invoke(["run", *common_args])
    if not run_result.success:
        raise RuntimeError(f"dbt run a échoué: {run_result.exception}")

    runner.invoke(["test", *common_args])


def _count_mart_rows() -> dict[str, int]:
    """Row counts per dbt mart after the transform, as a stand-in for "rows synced this run"
    (dlt's `LoadInfo` doesn't cheaply expose per-resource row counts across all destinations) --
    a reasonable proxy for "how much data is now available" shown on the dashboard."""
    counts: dict[str, int] = {}
    with get_engine().connect() as conn:
        for table in _MART_TABLES:
            try:
                row = conn.execute(text(f"select count(*) from marts.{table}")).fetchone()  # noqa: S608
                counts[table] = int(row[0]) if row else 0
            except ProgrammingError:
                # Postgres aborts the whole transaction on a failed statement (e.g. an
                # not-yet-created mart) - roll back so the next table's query isn't also
                # rejected as "current transaction is aborted".
                conn.rollback()
                counts[table] = 0
    return counts
