from datetime import date

from fastapi import APIRouter

from app.api.deps import PlanServiceDep
from app.api.schemas.plan import PhaseBoundsRead, TrainingPlanRead, TrainingPlanUpdate
from app.core.config import get_settings
from app.domain.entities import TrainingPlan
from app.domain.phase import compute_phase, compute_phase_bounds

router = APIRouter(prefix="/api/plan", tags=["plan"])


def _to_read(plan: TrainingPlan) -> TrainingPlanRead:
    phase_info = compute_phase(plan.race_date, date.today())
    bounds = compute_phase_bounds(plan.race_date)
    return TrainingPlanRead(
        id=plan.id or "",
        name=plan.name,
        race_date=plan.race_date,
        target_time_seconds=plan.target_time_seconds,
        weeks_to_race=phase_info.weeks_to_race,
        phase=phase_info.phase.value,
        phases=[PhaseBoundsRead(phase=b.phase.value, start=b.start, end=b.end) for b in bounds],
    )


def _default_target_seconds() -> int | None:
    settings = get_settings()
    if not settings.marathon_target_time:
        return None
    hours, minutes, seconds = (int(p) for p in settings.marathon_target_time.split(":"))
    return hours * 3600 + minutes * 60 + seconds


@router.get("", response_model=TrainingPlanRead)
def get_plan(plan_service: PlanServiceDep) -> TrainingPlanRead:
    settings = get_settings()
    plan = plan_service.get_or_create_default(
        date.fromisoformat(settings.marathon_race_date), _default_target_seconds()
    )
    return _to_read(plan)


@router.post("", response_model=TrainingPlanRead)
def update_plan(payload: TrainingPlanUpdate, plan_service: PlanServiceDep) -> TrainingPlanRead:
    plan = plan_service.update_plan(
        TrainingPlan(
            id=None,
            name=payload.name,
            race_date=payload.race_date,
            target_time_seconds=payload.target_time_seconds,
        )
    )
    return _to_read(plan)
