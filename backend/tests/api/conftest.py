"""Points DUCKDB_PATH/GARMIN_TOKEN_STORE at a fresh temp dir *before* anything imports
`app.core.config` (whose `get_settings()` is `@lru_cache`d), since fixtures run too late for
that -- module-level code in a conftest.py is guaranteed to execute before sibling test modules
are collected/imported, env vars included.
"""

import os
import tempfile
from pathlib import Path

_tmp_dir = Path(tempfile.mkdtemp(prefix="training-partner-test-"))
os.environ["DUCKDB_PATH"] = str(_tmp_dir / "test.duckdb")
os.environ["GARMIN_TOKEN_STORE"] = str(_tmp_dir / "garmin_tokens")
os.environ.setdefault("MARATHON_RACE_DATE", "2027-04-11")

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    # Entering the TestClient as a context manager runs FastAPI's lifespan, which applies the
    # Alembic migrations against the temp DuckDB file (see app/main.py::_run_migrations).
    with TestClient(app) as test_client:
        yield test_client
