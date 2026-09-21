from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    garmin_email: str = ""
    garmin_password: str = ""
    garmin_token_store: str = str(BACKEND_DIR / ".garmin_tokens")

    # SQLAlchemy engine URL (app-owned tables + WarehouseReader). Postgres via Docker Compose
    # (see docker-compose.yml) - one database, several schemas (app/raw/staging/marts).
    database_url: str = "postgresql+psycopg://athlete:athlete@localhost:5432/athlete"

    # Discrete Postgres fields, used to build the plain `postgres://` URL dlt's postgres
    # destination expects (distinct from SQLAlchemy's `postgresql+psycopg://` dialect URL
    # above) and to feed dbt's profiles.yml via env_var().
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "athlete"
    postgres_password: str = "athlete"
    postgres_db: str = "athlete"

    marathon_race_date: str = "2027-04-11"
    marathon_target_time: str | None = None

    cors_origins: list[str] = ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
