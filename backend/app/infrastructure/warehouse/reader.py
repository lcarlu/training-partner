from datetime import date, datetime

import duckdb
from sqlalchemy.pool import PoolProxiedConnection

from app.domain.entities import Activity, Sport, WellnessDay
from app.infrastructure.warehouse.connection import get_warehouse_connection


def _table_missing(exc: Exception) -> bool:
    return isinstance(exc, duckdb.CatalogException)


def _row_to_activity(row: tuple) -> Activity:
    (
        activity_id,
        sport,
        name,
        start_time,
        duration_s,
        distance_m,
        avg_hr,
        max_hr,
        calories,
        elevation_gain_m,
        te_aerobic,
        te_anaerobic,
    ) = row
    try:
        sport_enum = Sport(sport)
    except ValueError:
        sport_enum = Sport.OTHER

    return Activity(
        id=str(activity_id),
        sport=sport_enum,
        name=name or "",
        start_time=(
            start_time
            if isinstance(start_time, datetime)
            else datetime.fromisoformat(str(start_time))
        ),
        duration_s=float(duration_s) if duration_s is not None else 0.0,
        distance_m=distance_m,
        avg_hr=avg_hr,
        max_hr=max_hr,
        calories=calories,
        elevation_gain_m=elevation_gain_m,
        training_effect_aerobic=te_aerobic,
        training_effect_anaerobic=te_anaerobic,
    )


def _row_to_wellness(row: tuple) -> WellnessDay:
    return WellnessDay(
        day=row[0] if isinstance(row[0], date) else date.fromisoformat(str(row[0])),
        resting_hr=row[1],
        hrv_status=row[2],
        hrv_last_night_avg=row[3],
        body_battery_min=row[4],
        body_battery_max=row[5],
        stress_avg=row[6],
        sleep_score=row[7],
        sleep_duration_s=row[8],
        vo2max_running=row[9],
        vo2max_cycling=row[10],
        training_readiness_score=row[11],
        training_status=row[12],
    )


class WarehouseReader:
    """Read-only access to the dbt marts (`marts.fct_activities`, `marts.fct_daily_wellness`,
    `marts.agg_weekly_volume_by_sport`). Returns empty results if a mart doesn't exist yet
    (e.g. before the first sync has ever run)."""

    def __init__(self, conn: PoolProxiedConnection | None = None):
        self.conn = conn or get_warehouse_connection()

    def list_activities(
        self,
        sport: Sport | None = None,
        since: date | None = None,
        until: date | None = None,
        limit: int = 100,
    ) -> list[Activity]:
        query = (
            "select activity_id, sport, name, start_time, duration_s, distance_m, avg_hr, "
            "max_hr, calories, elevation_gain_m, training_effect_aerobic, "
            "training_effect_anaerobic "
            "from marts.fct_activities where 1=1"
        )
        params: list = []
        if sport is not None:
            query += " and sport = ?"
            params.append(sport.value)
        if since is not None:
            query += " and start_time >= ?"
            params.append(since)
        if until is not None:
            query += " and start_time <= ?"
            params.append(until)
        query += " order by start_time desc limit ?"
        params.append(limit)
        try:
            rows = self.conn.execute(query, params).fetchall()
        except duckdb.CatalogException:
            return []
        return [_row_to_activity(r) for r in rows]

    def get_activity(self, activity_id: str) -> Activity | None:
        query = (
            "select activity_id, sport, name, start_time, duration_s, distance_m, avg_hr, "
            "max_hr, calories, elevation_gain_m, training_effect_aerobic, "
            "training_effect_anaerobic "
            "from marts.fct_activities where activity_id = ?"
        )
        try:
            row = self.conn.execute(query, [activity_id]).fetchone()
        except duckdb.CatalogException:
            return None
        return _row_to_activity(row) if row else None

    def weekly_volume_by_sport(self, weeks: int = 12) -> list[dict]:
        query = (
            "select week_start, sport, total_distance_km, total_duration_h, activity_count "
            "from marts.agg_weekly_volume_by_sport order by week_start desc limit ?"
        )
        try:
            rows = self.conn.execute(query, [weeks * 5]).fetchall()
        except duckdb.CatalogException:
            return []
        return [
            {
                "week_start": str(r[0]),
                "sport": r[1],
                "total_distance_km": r[2],
                "total_duration_h": r[3],
                "activity_count": r[4],
            }
            for r in rows
        ]

    def list_daily_wellness(self, since: date, until: date) -> list[WellnessDay]:
        query = (
            "select day, resting_hr, hrv_status, hrv_last_night_avg, body_battery_min, "
            "body_battery_max, stress_avg, sleep_score, sleep_duration_s, vo2max_running, "
            "vo2max_cycling, training_readiness_score, training_status "
            "from marts.fct_daily_wellness where day >= ? and day <= ? order by day asc"
        )
        try:
            rows = self.conn.execute(query, [since, until]).fetchall()
        except duckdb.CatalogException:
            return []
        return [_row_to_wellness(r) for r in rows]

    def latest_wellness(self) -> WellnessDay | None:
        query = (
            "select day, resting_hr, hrv_status, hrv_last_night_avg, body_battery_min, "
            "body_battery_max, stress_avg, sleep_score, sleep_duration_s, vo2max_running, "
            "vo2max_cycling, training_readiness_score, training_status "
            "from marts.fct_daily_wellness order by day desc limit 1"
        )
        try:
            row = self.conn.execute(query).fetchone()
        except duckdb.CatalogException:
            return None
        return _row_to_wellness(row) if row else None
