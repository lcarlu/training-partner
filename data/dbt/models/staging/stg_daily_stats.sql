-- Best-guess column names, see stg_activities.sql for the caveat.

select
    day,
    resting_heart_rate as resting_hr
from {{ source('raw', 'daily_stats') }}
