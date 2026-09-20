from datetime import date

from fastapi import APIRouter, HTTPException

from app.api.deps import WarehouseReaderDep
from app.api.schemas.activity import ActivityListResponse, ActivityRead
from app.domain.entities import Sport

router = APIRouter(prefix="/api/activities", tags=["activities"])


@router.get("", response_model=ActivityListResponse)
def list_activities(
    reader: WarehouseReaderDep,
    sport: Sport | None = None,
    since: date | None = None,
    until: date | None = None,
    limit: int = 100,
) -> ActivityListResponse:
    activities = reader.list_activities(sport=sport, since=since, until=until, limit=limit)
    items = [ActivityRead.model_validate(a) for a in activities]
    return ActivityListResponse(items=items, total=len(items))


@router.get("/{activity_id}", response_model=ActivityRead)
def get_activity(activity_id: str, reader: WarehouseReaderDep) -> ActivityRead:
    activity = reader.get_activity(activity_id)
    if activity is None:
        raise HTTPException(status_code=404, detail="Activité introuvable")
    return ActivityRead.model_validate(activity)
