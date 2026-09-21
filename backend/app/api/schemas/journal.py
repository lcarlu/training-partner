from datetime import date

from pydantic import Field

from app.api.schemas.base import CamelModel
from app.domain.entities import Sport


class JournalEntryCreate(CamelModel):
    day: date = Field(alias="date")
    sport: Sport = Sport.RUNNING
    planned_notes: str | None = None
    actual_notes: str | None = None
    rpe: int | None = None
    mood: int | None = None
    linked_activity_id: str | None = None


class JournalEntryRead(JournalEntryCreate):
    id: str
