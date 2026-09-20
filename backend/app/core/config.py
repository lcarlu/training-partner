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

    duckdb_path: str = str(PROJECT_ROOT / "data" / "warehouse.duckdb")

    marathon_race_date: str = "2027-04-11"
    marathon_target_time: str | None = None

    cors_origins: list[str] = ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
