-- NOTE: column names are best-guess from garminconnect's documented field names, snake_cased
-- by dlt. Not verified against a live sync (see garmin_pipeline.py docstring) -- this is the
-- first model to fix once real `raw.activities` data lands, by inspecting
-- `describe raw.activities` in DuckDB.

select
    activity_id,
    lower(coalesce(activity_type__type_key, 'other')) as sport_raw,
    activity_name as name,
    cast(start_time_local as timestamp) as start_time,
    duration as duration_s,
    distance as distance_m,
    average_hr as avg_hr,
    max_hr,
    calories,
    elevation_gain as elevation_gain_m,
    aerobic_training_effect as training_effect_aerobic,
    anaerobic_training_effect as training_effect_anaerobic
from {{ source('raw', 'activities') }}
