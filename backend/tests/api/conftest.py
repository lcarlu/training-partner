"""Points DATABASE_URL/GARMIN_TOKEN_STORE at a dedicated test database *before* anything
imports `app.core.config` (whose `get_settings()` is `@lru_cache`d), since fixtures run too
late for that -- module-level code in a conftest.py is guaranteed to execute before sibling
test modules are collected/imported, env vars included.

Uses the same Postgres server as dev (see docker-compose.yml at the repo root), a separate
`athlete_test` database recreated fresh each test session for isolation.
"""

import os
import sys
import tempfile
from pathlib import Path

_PG_HOST = os.environ.get("POSTGRES_HOST", "localhost")
_PG_PORT = os.environ.get("POSTGRES_PORT", "5432")
_PG_USER = os.environ.get("POSTGRES_USER", "athlete")
_PG_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "athlete")
_PG_ADMIN_DB = os.environ.get("POSTGRES_DB", "athlete")
_TEST_DB = "athlete_test"

try:
    import psycopg

    with psycopg.connect(
        host=_PG_HOST,
        port=_PG_PORT,
        user=_PG_USER,
        password=_PG_PASSWORD,
        dbname=_PG_ADMIN_DB,
        autocommit=True,
        connect_timeout=5,
    ) as admin_conn:
        admin_conn.execute(f"DROP DATABASE IF EXISTS {_TEST_DB} WITH (FORCE)")
        admin_conn.execute(f"CREATE DATABASE {_TEST_DB}")
except Exception as exc:  # noqa: BLE001
    print(
        f"\n[!] Impossible de joindre Postgres ({_PG_HOST}:{_PG_PORT}) pour créer la base de "
        f"test '{_TEST_DB}': {exc!r}\n    Lance `docker compose up -d` depuis la racine du "
        "projet avant de lancer les tests.\n",
        file=sys.stderr,
    )
    raise

_tmp_dir = Path(tempfile.mkdtemp(prefix="training-partner-test-"))
os.environ["DATABASE_URL"] = (
    f"postgresql+psycopg://{_PG_USER}:{_PG_PASSWORD}@{_PG_HOST}:{_PG_PORT}/{_TEST_DB}"
)
os.environ["GARMIN_TOKEN_STORE"] = str(_tmp_dir / "garmin_tokens")
os.environ.setdefault("MARATHON_RACE_DATE", "2027-04-11")

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    # Entering the TestClient as a context manager runs FastAPI's lifespan, which applies the
    # Alembic migrations against athlete_test (see app/main.py::_run_migrations).
    with TestClient(app) as test_client:
        yield test_client
