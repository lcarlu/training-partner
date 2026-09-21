from collections import defaultdict
from datetime import date, timedelta

from app.api.schemas.dashboard import DashboardSummary, RecommendationRead, WeeklyVolumePoint
from app.api.schemas.wellness import WellnessDayRead
from app.domain.entities import Recommendation, Sport, TrainingPlan
from app.domain.phase import compute_phase
from app.domain.recommendations import generate_recommendations
from app.infrastructure.db.models import SyncLog
from app.infrastructure.warehouse.reader import WarehouseReader

_WELLNESS_LOOKBACK_DAYS = 14
_VOLUME_LOOKBACK_WEEKS = 8


def build_recommendations(
    plan: TrainingPlan | None,
    wellness_reader: WarehouseReader,
    activity_reader: WarehouseReader,
    today: date | None = None,
) -> list[Recommendation]:
    if plan is None:
        return []

    today = today or date.today()
    phase_info = compute_phase(plan.race_date, today)
    recent_wellness = wellness_reader.list_daily_wellness(
        today - timedelta(days=_WELLNESS_LOOKBACK_DAYS), today
    )
    weekly_rows = activity_reader.weekly_volume_by_sport(weeks=_VOLUME_LOOKBACK_WEEKS)
    weekly_km = _aggregate_weekly_km(weekly_rows)

    return generate_recommendations(phase_info, recent_wellness, weekly_km)


def _aggregate_weekly_km(weekly_rows: list[dict]) -> list[float]:
    totals: dict[str, float] = defaultdict(float)
    for row in weekly_rows:
        totals[row["week_start"]] += row["total_distance_km"] or 0.0
    return [totals[week] for week in sorted(totals)]


def _pivot_weekly_volume(weekly_rows: list[dict], sport: Sport | None) -> list[WeeklyVolumePoint]:
    """Flat {week_start, sport, total_duration_h, ...} rows from the mart -> one point per week
    with a `{sport: minutes}` breakdown, optionally restricted to a single sport."""
    by_week: dict[str, dict[str, float]] = defaultdict(dict)
    for row in weekly_rows:
        if sport is not None and row["sport"] != sport.value:
            continue
        by_week[row["week_start"]][row["sport"]] = round((row["total_duration_h"] or 0.0) * 60, 1)
    return [WeeklyVolumePoint(week_start=week, by_sport=by_week[week]) for week in sorted(by_week)]


def build_dashboard_summary(
    plan: TrainingPlan,
    reader: WarehouseReader,
    sync_log: SyncLog | None,
    sport: Sport | None = None,
) -> DashboardSummary:
    today = date.today()
    phase_info = compute_phase(plan.race_date, today)

    recent_wellness = reader.list_daily_wellness(
        today - timedelta(days=_WELLNESS_LOOKBACK_DAYS), today
    )
    weekly_rows = reader.weekly_volume_by_sport(weeks=_VOLUME_LOOKBACK_WEEKS)
    today_wellness = reader.latest_wellness()
    recommendations = build_recommendations(plan, reader, reader, today)

    return DashboardSummary(
        race_date=plan.race_date.isoformat(),
        days_until_race=(plan.race_date - today).days,
        phase=phase_info.phase.value,
        weekly_volume=_pivot_weekly_volume(weekly_rows, sport),
        recent_wellness=[WellnessDayRead.model_validate(w) for w in recent_wellness],
        today_wellness=WellnessDayRead.model_validate(today_wellness) if today_wellness else None,
        recommendations=[
            RecommendationRead(id=str(i), severity=r.severity.value, title=r.title, detail=r.detail)
            for i, r in enumerate(recommendations)
        ],
        last_sync_at=sync_log.finished_at if sync_log else None,
    )
