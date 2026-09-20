"""Orchestrates the sync: dlt extract (Garmin -> DuckDB `raw`) then dbt transform
(`raw` -> `staging` -> `marts`), both in-process (no separate CLI subprocess) and serialized
behind the shared sync lock so only this one process ever touches the DuckDB file at a time.
"""

import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlmodel import Session

from app.core.db import get_engine
from app.infrastructure.db.repositories import SqlSyncLogRepository
from app.infrastructure.warehouse.connection import get_sync_lock

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

    async with get_sync_lock():
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
    from dbt.cli.main import dbtRunner

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
    import duckdb

    conn = get_engine().raw_connection()
    counts: dict[str, int] = {}
    for table in _MART_TABLES:
        try:
            (n,) = conn.execute(f"select count(*) from marts.{table}").fetchone()  # noqa: S608
            counts[table] = int(n)
        except duckdb.CatalogException:
            counts[table] = 0
    return counts
