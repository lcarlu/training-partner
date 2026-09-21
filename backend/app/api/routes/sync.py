from fastapi import APIRouter, HTTPException

from app.api.schemas.sync import SyncSummary
from app.infrastructure.garmin.client import GarminAuthError
from app.services.sync_service import execute_sync_refresh

router = APIRouter(prefix="/api/sync", tags=["sync"])


@router.post("/refresh", response_model=SyncSummary)
async def refresh() -> SyncSummary:
    try:
        result = await execute_sync_refresh()
    except GarminAuthError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return SyncSummary.model_validate(result)
