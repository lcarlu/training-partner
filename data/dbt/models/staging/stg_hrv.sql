-- Best-guess column names, see stg_activities.sql for the caveat.

select
    day,
    hrv_summary__status as hrv_status,
    hrv_summary__last_night_avg as hrv_last_night_avg
from {{ source('raw', 'hrv') }}
