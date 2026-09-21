from datetime import date

from pydantic import Field

from app.api.schemas.base import CamelModel


class WellnessDayRead(CamelModel):
    day: date = Field(alias="date")
    resting_hr: int | None = Field(alias="restingHeartRate")
    hrv_status: str | None
    hrv_last_night_avg: float | None = Field(alias="hrvValueMs")
    body_battery_min: int | None
    body_battery_max: int | None
    stress_avg: int | None
    sleep_score: int | None
    sleep_duration_s: float | None = Field(alias="sleepDurationSeconds")
    vo2max_running: float | None = Field(alias="vo2max")
    """Only the running VO2max is exposed in v1 (marathon focus); `vo2max_cycling` stays
    internal until a cycling-specific view is built."""
    training_readiness_score: int | None
    training_status: str | None
