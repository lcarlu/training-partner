import asyncio
from functools import lru_cache

from sqlalchemy.pool import PoolProxiedConnection

from app.core.db import get_engine

_sync_lock = asyncio.Lock()


@lru_cache
def get_warehouse_connection() -> PoolProxiedConnection:
    """Single shared DuckDB connection for this process, reused from the same SQLAlchemy engine
    that backs the app-owned tables (see app/core/db.py::get_engine) rather than opened
    independently: DuckDB refuses a second `duckdb.connect()` to the same file within one process
    when its configuration doesn't exactly match an already-open connection's, which a bare
    `duckdb.connect(path)` alongside duckdb-engine's connection reliably triggers.

    dlt (extract) and dbt (transform) are invoked in-process (see pipeline_runner) rather than
    as separate CLI subprocesses, and uvicorn must run with a single worker: DuckDB only allows
    one process to hold the file open for read/write at a time. `get_sync_lock` serializes the
    write-heavy refresh phase against journal/plan CRUD and warehouse reads within this process.

    Not yet exercised against a real sync (no Garmin credentials in dev): if dlt/dbt's own
    internal connections turn out to conflict with this long-lived one the same way, the fix is
    for `pipeline_runner` to close/clear this connection before running dlt+dbt and let it
    reopen lazily afterwards, under the same sync lock.
    """
    # SQLAlchemy's raw_connection() proxies attribute access down to the native
    # duckdb.DuckDBPyConnection (via duckdb_engine.ConnectionWrapper.__getattr__), so
    # `.execute(...).fetchall()`/`.fetchone()` work exactly as they would on a bare connection.
    return get_engine().raw_connection()


def get_sync_lock() -> asyncio.Lock:
    return _sync_lock
