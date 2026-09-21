from datetime import datetime

from app.api.schemas.base import CamelModel
from app.api.schemas.wellness import WellnessDayRead


class RecommendationRead(CamelModel):
    id: str
    severity: str
    title: str
    detail: str


class WeeklyVolumePoint(CamelModel):
    week_start: str
    by_sport: dict[str, float]
    """Minutes of training per sport for that week (`total_duration_h * 60` from the mart)."""


class DashboardSummary(CamelModel):
    race_date: str
    days_until_race: int
    phase: str
    weekly_volume: list[WeeklyVolumePoint]
    recent_wellness: list[WellnessDayRead]
    today_wellness: WellnessDayRead | None
    recommendations: list[RecommendationRead]
    last_sync_at: datetime | None
