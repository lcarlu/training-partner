-- `vo2max_running`/`vo2max_cycling`/`training_status` are already flattened in the dlt
-- resource (garmin_pipeline.py) since the raw payload nests the status under a per-account
-- device id dlt can't turn into a stable column name.

select
    day::date as day,
    vo2max_running,
    vo2max_cycling,
    training_status
from {{ source('raw', 'training_status') }}
