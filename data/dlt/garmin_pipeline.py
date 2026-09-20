"""dlt source: extracts Garmin Connect data into the DuckDB `raw` dataset, incrementally.

Each resource tracks its own sync watermark via `dlt.sources.incremental`, so a run only
calls the Garmin API for days/activities that haven't been synced yet. dbt then transforms
`raw` into `staging`/`marts` (see ../dbt).

NOTE: garminconnect's exact response shapes for sleep/HRV/stress/training status/etc. are not
officially documented and can vary by account/device. This pipeline was written against the
method signatures of the installed `garminconnect` version (checked via introspection) but
NOT against live API responses (no Garmin credentials were available while building this).
The dbt staging models should be treated as the first thing to adjust once real data lands,
in case of a field-name mismatch.
"""

import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import dlt

BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import get_settings  # noqa: E402
from app.infrastructure.garmin.client import build_client  # noqa: E402

DEFAULT_START_DATE = "2024-01-01"


def _day_range(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def _start_day(incremental: dlt.sources.incremental) -> date:
    if incremental.last_value:
        return date.fromisoformat(str(incremental.last_value)) + timedelta(days=1)
    return date.fromisoformat(DEFAULT_START_DATE)


@dlt.source(name="garmin")
def garmin_source(client: Any = None):
    client = client or build_client()
    today = date.today()

    @dlt.resource(name="activities", write_disposition="merge", primary_key="activityId")
    def activities(
        updated=dlt.sources.incremental(
            "startTimeLocal", initial_value=f"{DEFAULT_START_DATE} 00:00:00"
        ),
    ):
        start = (
            str(updated.last_value)[:10] if updated.last_value else DEFAULT_START_DATE
        )
        yield client.get_activities_by_date(start, today.isoformat())

    @dlt.resource(name="daily_stats", write_disposition="merge", primary_key="day")
    def daily_stats(day_cursor=dlt.sources.incremental("day", initial_value=DEFAULT_START_DATE)):
        for d in _day_range(_start_day(day_cursor), today):
            stats = _safe_call(client.get_stats, d.isoformat())
            if stats:
                stats["day"] = d.isoformat()
                yield stats

    @dlt.resource(name="sleep", write_disposition="merge", primary_key="day")
    def sleep(day_cursor=dlt.sources.incremental("day", initial_value=DEFAULT_START_DATE)):
        for d in _day_range(_start_day(day_cursor), today):
            data = _safe_call(client.get_sleep_data, d.isoformat())
            if data:
                data["day"] = d.isoformat()
                yield data

    @dlt.resource(name="hrv", write_disposition="merge", primary_key="day")
    def hrv(day_cursor=dlt.sources.incremental("day", initial_value=DEFAULT_START_DATE)):
        for d in _day_range(_start_day(day_cursor), today):
            data = _safe_call(client.get_hrv_data, d.isoformat())
            if data:
                data["day"] = d.isoformat()
                yield data

    @dlt.resource(name="stress", write_disposition="merge", primary_key="day")
    def stress(day_cursor=dlt.sources.incremental("day", initial_value=DEFAULT_START_DATE)):
        for d in _day_range(_start_day(day_cursor), today):
            data = _safe_call(client.get_stress_data, d.isoformat())
            if data:
                data["day"] = d.isoformat()
                yield data

    @dlt.resource(name="training_readiness", write_disposition="merge", primary_key="day")
    def training_readiness(
        day_cursor=dlt.sources.incremental("day", initial_value=DEFAULT_START_DATE),
    ):
        for d in _day_range(_start_day(day_cursor), today):
            data = _safe_call(client.get_training_readiness, d.isoformat())
            if data:
                entry = data[0] if isinstance(data, list) and data else data
                if entry:
                    entry["day"] = d.isoformat()
                    yield entry

    @dlt.resource(name="training_status", write_disposition="merge", primary_key="day")
    def training_status(
        day_cursor=dlt.sources.incremental("day", initial_value=DEFAULT_START_DATE),
    ):
        for d in _day_range(_start_day(day_cursor), today):
            data = _safe_call(client.get_training_status, d.isoformat())
            if data:
                data["day"] = d.isoformat()
                yield data

    @dlt.resource(name="max_metrics", write_disposition="merge", primary_key="day")
    def max_metrics(day_cursor=dlt.sources.incremental("day", initial_value=DEFAULT_START_DATE)):
        for d in _day_range(_start_day(day_cursor), today):
            data = _safe_call(client.get_max_metrics, d.isoformat())
            if data:
                data["day"] = d.isoformat()
                yield data

    @dlt.resource(name="body_battery", write_disposition="merge", primary_key="calendarDate")
    def body_battery(
        day_cursor=dlt.sources.incremental("calendarDate", initial_value=DEFAULT_START_DATE),
    ):
        start = _start_day(day_cursor)
        if start > today:
            return
        yield client.get_body_battery(start.isoformat(), today.isoformat())

    @dlt.resource(name="body_composition", write_disposition="merge", primary_key="day")
    def body_composition(
        day_cursor=dlt.sources.incremental("day", initial_value=DEFAULT_START_DATE),
    ):
        start = _start_day(day_cursor)
        if start > today:
            return
        result = _safe_call(client.get_body_composition, start.isoformat(), today.isoformat())
        for entry in (result or {}).get("dateWeightList", []) or []:
            entry["day"] = entry.get("date") or entry.get("calendarDate")
            if entry["day"]:
                yield entry

    @dlt.resource(name="race_predictions", write_disposition="merge", primary_key="day")
    def race_predictions():
        data = _safe_call(client.get_race_predictions)
        if data:
            data["day"] = today.isoformat()
            yield data

    return (
        activities,
        daily_stats,
        sleep,
        hrv,
        stress,
        training_readiness,
        training_status,
        max_metrics,
        body_battery,
        body_composition,
        race_predictions,
    )


def _safe_call(fn, *args: Any) -> Any:
    """Garmin returns errors (or empty payloads) for days with no data; skip rather than fail
    the whole sync over one bad day."""
    try:
        return fn(*args)
    except Exception:  # noqa: BLE001 - deliberately broad, see docstring
        return None


def run_pipeline() -> str:
    settings = get_settings()
    pipeline = dlt.pipeline(
        pipeline_name="garmin",
        destination=dlt.destinations.duckdb(settings.duckdb_path),
        dataset_name="raw",
    )
    load_info = pipeline.run(garmin_source())
    return str(load_info)


if __name__ == "__main__":
    print(run_pipeline())
