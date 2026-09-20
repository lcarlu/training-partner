from typing import Any

from app.infrastructure.warehouse.pipeline_runner import run_sync as _run_sync_pipeline


async def execute_sync_refresh() -> dict[str, Any]:
    """Use case: refresh Garmin data (dlt extract -> dbt transform) for the dashboard."""
    return await _run_sync_pipeline()
