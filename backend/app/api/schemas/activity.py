from datetime import datetime

from pydantic import Field, computed_field

from app.api.schemas.base import CamelModel
from app.domain.entities import Sport


class ActivityRead(CamelModel):
    id: str
    sport: Sport
    name: str
    start_time: datetime
    duration_s: float = Field(alias="durationSeconds")
    distance_m: float | None = Field(alias="distanceMeters")
    avg_hr: int | None = Field(alias="avgHeartRate")
    max_hr: int | None = Field(alias="maxHeartRate")
    calories: float | None
    elevation_gain_m: float | None = Field(alias="elevationGainMeters")
    training_effect_aerobic: float | None
    training_effect_anaerobic: float | None

    @computed_field(alias="avgPaceSecPerKm")  # type: ignore[prop-decorator]
    @property
    def avg_pace_sec_per_km(self) -> float | None:
        if self.distance_m and self.distance_m > 0:
            return self.duration_s / (self.distance_m / 1000)
        return None


class ActivityListResponse(CamelModel):
    items: list[ActivityRead]
    total: int
    """`total` == `len(items)` for v1 (no independent count query beyond `limit`);
    real offset/count pagination is a fast-follow."""
