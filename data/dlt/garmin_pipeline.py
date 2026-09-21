"""dlt source: extracts Garmin Connect data into the Postgres `raw` schema, incrementally.

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

import re
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

# On the very first sync there's no incremental watermark yet, so every resource falls back
# to this lookback window. Two reasons to keep it short rather than reaching years back:
# 1. The day-granularity resources (sleep, HRV, stress, training readiness/status, VO2max,
#    daily stats) call the Garmin API once PER DAY in the initial range - a ~1000-day
#    backfill means ~7000 sequential calls, slow enough to hang the request and get
#    rate-limited by Garmin.
# 2. Even the range-based resources (body_battery, body_composition, activities) can be
#    rejected outright by Garmin with "requested date range is too big" for a multi-year span.
# A wider historical backfill is a deliberate fast-follow (e.g. a separate, paced backfill
# command that chunks the range), not part of the every-page-load refresh.
INITIAL_SYNC_LOOKBACK_DAYS = 30


def _default_sync_start() -> str:
    return (date.today() - timedelta(days=INITIAL_SYNC_LOOKBACK_DAYS)).isoformat()


def _day_range(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def _start_day(incremental: dlt.sources.incremental) -> date:
    if incremental.last_value:
        return date.fromisoformat(str(incremental.last_value)) + timedelta(days=1)
    return date.fromisoformat(_default_sync_start())


@dlt.source(name="garmin")
def garmin_source(client: Any = None):
    client = client or build_client()
    today = date.today()

    @dlt.resource(name="activities", write_disposition="merge", primary_key="activityId")
    def activities(
        updated=dlt.sources.incremental(
            "startTimeLocal", initial_value=f"{_default_sync_start()} 00:00:00"
        ),
    ):
        start = str(updated.last_value)[:10] if updated.last_value else _default_sync_start()
        yield client.get_activities_by_date(start, today.isoformat())

    @dlt.resource(name="daily_stats", write_disposition="merge", primary_key="day")
    def daily_stats(
        day_cursor=dlt.sources.incremental("day", initial_value=_default_sync_start()),
    ):
        for d in _day_range(_start_day(day_cursor), today):
            stats = _safe_call(client.get_stats, d.isoformat())
            if stats:
                stats["day"] = d.isoformat()
                yield stats

    @dlt.resource(name="sleep", write_disposition="merge", primary_key="day")
    def sleep(day_cursor=dlt.sources.incremental("day", initial_value=_default_sync_start())):
        for d in _day_range(_start_day(day_cursor), today):
            data = _safe_call(client.get_sleep_data, d.isoformat())
            if data:
                data["day"] = d.isoformat()
                yield data

    @dlt.resource(name="hrv", write_disposition="merge", primary_key="day")
    def hrv(day_cursor=dlt.sources.incremental("day", initial_value=_default_sync_start())):
        for d in _day_range(_start_day(day_cursor), today):
            data = _safe_call(client.get_hrv_data, d.isoformat())
            if data:
                data["day"] = d.isoformat()
                yield data

    @dlt.resource(name="stress", write_disposition="merge", primary_key="day")
    def stress(day_cursor=dlt.sources.incremental("day", initial_value=_default_sync_start())):
        for d in _day_range(_start_day(day_cursor), today):
            data = _safe_call(client.get_stress_data, d.isoformat())
            if data:
                data["day"] = d.isoformat()
                yield data

    @dlt.resource(name="training_readiness", write_disposition="merge", primary_key="day")
    def training_readiness(
        day_cursor=dlt.sources.incremental("day", initial_value=_default_sync_start()),
    ):
        for d in _day_range(_start_day(day_cursor), today):
            data = _safe_call(client.get_training_readiness, d.isoformat())
            if data:
                entry = data[0] if isinstance(data, list) and data else data
                if entry:
                    entry["day"] = d.isoformat()
                    yield entry

    @dlt.resource(
        name="training_status",
        write_disposition="merge",
        primary_key="day",
        # Force these columns to always materialize even if every row in a batch has NULL
        # (e.g. a runner with no cycling VO2max ever) - dlt otherwise drops untyped all-NULL
        # columns, which then breaks dbt models that reference them by name.
        columns={
            "vo2max_running": {"data_type": "double", "nullable": True},
            "vo2max_cycling": {"data_type": "double", "nullable": True},
            "training_status": {"data_type": "text", "nullable": True},
        },
    )
    def training_status(
        day_cursor=dlt.sources.incremental("day", initial_value=_default_sync_start()),
    ):
        # Verified against a live account: `get_training_status(day)` nests VO2max under
        # `mostRecentVO2Max.generic`/`.cycling`, and the training status label under
        # `mostRecentTrainingStatus.latestTrainingStatusData.<deviceId>` - keyed by a
        # per-account device id we can't know ahead of time, so dlt's automatic flattening
        # can't produce a stable column name for it. Flatten by hand instead.
        for d in _day_range(_start_day(day_cursor), today):
            data = _safe_call(client.get_training_status, d.isoformat())
            if not data:
                continue
            entry: dict[str, Any] = {"day": d.isoformat()}

            vo2max = data.get("mostRecentVO2Max") or {}
            entry["vo2max_running"] = (vo2max.get("generic") or {}).get("vo2MaxValue")
            entry["vo2max_cycling"] = (vo2max.get("cycling") or {}).get("vo2MaxValue")

            by_device = (data.get("mostRecentTrainingStatus") or {}).get(
                "latestTrainingStatusData"
            ) or {}
            device_status = next(iter(by_device.values()), None)
            if device_status:
                # e.g. "PRODUCTIVE_3" -> "PRODUCTIVE" (trailing number is an intensity
                # sub-level, not part of the status itself).
                phrase = device_status.get("trainingStatusFeedbackPhrase") or ""
                entry["training_status"] = re.sub(r"_\d+$", "", phrase) or None

            yield entry

    @dlt.resource(name="max_metrics", write_disposition="merge", primary_key="day")
    def max_metrics(
        day_cursor=dlt.sources.incremental("day", initial_value=_default_sync_start()),
    ):
        for d in _day_range(_start_day(day_cursor), today):
            data = _safe_call(client.get_max_metrics, d.isoformat())
            # Garmin returns a list here (often empty - VO2max isn't updated every day),
            # unlike most other daily endpoints which return a single dict.
            entry = data[0] if isinstance(data, list) and data else data
            if entry:
                entry["day"] = d.isoformat()
                yield entry

    @dlt.resource(name="body_battery", write_disposition="merge", primary_key="date")
    def body_battery(
        day_cursor=dlt.sources.incremental("date", initial_value=_default_sync_start()),
    ):
        start = _start_day(day_cursor)
        if start > today:
            return
        # Verified against a live account: each entry's date field is `date` (not
        # `calendarDate`), and there's no ready-made min/max battery level - only `charged`/
        # `drained` totals plus a `bodyBatteryValuesArray` of [timestamp_ms, level] samples,
        # which we reduce to min/max ourselves.
        result = _safe_call(client.get_body_battery, start.isoformat(), today.isoformat())
        for entry in result or []:
            samples = entry.get("bodyBatteryValuesArray") or []
            levels = [s[1] for s in samples if isinstance(s, list) and len(s) == 2]
            if levels:
                entry["body_battery_min"] = min(levels)
                entry["body_battery_max"] = max(levels)
        if result:
            yield result

    @dlt.resource(name="body_composition", write_disposition="merge", primary_key="day")
    def body_composition(
        day_cursor=dlt.sources.incremental("day", initial_value=_default_sync_start()),
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
    # dlt's postgres destination takes a plain `postgres://` connection string (its own
    # credentials format, distinct from SQLAlchemy's `postgresql+psycopg://` dialect URL used
    # elsewhere in the app).
    credentials = (
        f"postgresql://{settings.postgres_user}:{settings.postgres_password}"
        f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
    )
    pipeline = dlt.pipeline(
        pipeline_name="garmin",
        destination=dlt.destinations.postgres(credentials=credentials),
        dataset_name="raw",
    )
    load_info = pipeline.run(garmin_source())
    return str(load_info)


if __name__ == "__main__":
    print(run_pipeline())
