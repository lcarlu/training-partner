from datetime import date, timedelta

from fastapi import APIRouter

from app.api.deps import WarehouseReaderDep
from app.api.schemas.wellness import WellnessDayRead

router = APIRouter(prefix="/api/wellness", tags=["wellness"])

_DEFAULT_LOOKBACK_DAYS = 30


@router.get("/daily", response_model=list[WellnessDayRead])
def list_daily_wellness(
    reader: WarehouseReaderDep,
    since: date | None = None,
    until: date | None = None,
) -> list[WellnessDayRead]:
    until = until or date.today()
    since = since or (until - timedelta(days=_DEFAULT_LOOKBACK_DAYS))
    days = reader.list_daily_wellness(since, until)
    return [WellnessDayRead.model_validate(d) for d in days]
