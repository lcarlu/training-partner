from datetime import date

from fastapi import APIRouter

from app.api.deps import PlanServiceDep, SyncLogRepositoryDep, WarehouseReaderDep
from app.api.schemas.dashboard import DashboardSummary
from app.core.config import get_settings
from app.domain.entities import Sport
from app.services.dashboard_service import build_dashboard_summary

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_summary(
    plan_service: PlanServiceDep,
    reader: WarehouseReaderDep,
    sync_log_repo: SyncLogRepositoryDep,
    sport: Sport | None = None,
) -> DashboardSummary:
    settings = get_settings()
    plan = plan_service.get_or_create_default(date.fromisoformat(settings.marathon_race_date), None)
    sync_log = sync_log_repo.get_latest()
    return build_dashboard_summary(plan, reader, sync_log, sport)
