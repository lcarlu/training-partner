from datetime import datetime

from app.api.schemas.base import CamelModel


class SyncSummary(CamelModel):
    started_at: datetime
    finished_at: datetime
    counts: dict[str, int]
