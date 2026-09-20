from datetime import date

from pydantic import Field

from app.api.schemas.base import CamelModel


class TrainingPlanUpdate(CamelModel):
    name: str = "Marathon"
    race_date: date
    target_time_seconds: int | None = None


class PhaseBoundsRead(CamelModel):
    phase: str
    start: date
    end: date


class TrainingPlanRead(CamelModel):
    id: str
    name: str
    race_date: date
    target_time_seconds: int | None
    weeks_to_race: float
    phase: str
    phases: list[PhaseBoundsRead] = Field(default_factory=list)
