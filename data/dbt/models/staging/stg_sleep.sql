-- Best-guess column names, see stg_activities.sql for the caveat.

select
    day::date as day,
    daily_sleep_dto__sleep_time_seconds as sleep_duration_s,
    daily_sleep_dto__sleep_scores__overall__value as sleep_score
from {{ source('raw', 'sleep') }}
