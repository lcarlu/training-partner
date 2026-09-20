import json
from datetime import date, datetime
from uuid import uuid4

from sqlmodel import Field, SQLModel

from app.core.db import APP_SCHEMA
from app.domain.entities import Sport


def _new_id() -> str:
    return uuid4().hex


class JournalEntry(SQLModel, table=True):
    """`id` is a client-generated UUID hex string rather than a DB-generated integer:
    the Postgres-derived duckdb-engine dialect renders integer autoincrement PKs as
    `SERIAL`, a type DuckDB doesn't implement, and Alembic autogenerate doesn't reliably
    emit `CREATE SEQUENCE` for this dialect either. A client-side id sidesteps both."""

    __tablename__ = "journal_entry"
    __table_args__ = {"schema": APP_SCHEMA}

    id: str = Field(default_factory=_new_id, primary_key=True)
    day: date = Field(index=True)
    sport: Sport = Field(default=Sport.RUNNING)
    planned_notes: str | None = None
    actual_notes: str | None = None
    rpe: int | None = None
    mood: int | None = None
    linked_activity_id: str | None = None


class TrainingPlan(SQLModel, table=True):
    __tablename__ = "training_plan"
    __table_args__ = {"schema": APP_SCHEMA}

    id: str = Field(default_factory=_new_id, primary_key=True)
    name: str = "Marathon"
    race_date: date
    target_time_seconds: int | None = None


class SyncLog(SQLModel, table=True):
    """Single always-overwritten row (`id="latest"`) recording the most recent sync run, so the
    dashboard can show `lastSyncAt`. `counts` is stored as a JSON *string* rather than a native
    JSON column: duckdb-engine's dialect has already shown SQL-generation gaps against
    Postgres-shaped SQLModel/Alembic output (see the id-column comment on `JournalEntry` above),
    so a plain TEXT column sidesteps another possible one."""

    __tablename__ = "sync_log"
    __table_args__ = {"schema": APP_SCHEMA}

    id: str = Field(default="latest", primary_key=True)
    started_at: datetime
    finished_at: datetime
    counts_json: str = "{}"

    @property
    def counts(self) -> dict[str, int]:
        return json.loads(self.counts_json)
