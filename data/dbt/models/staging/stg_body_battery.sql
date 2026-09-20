-- Best-guess column names, see stg_activities.sql for the caveat. `get_body_battery` returns
-- one row per day with min/max charge fields; exact names to confirm against real data.

select
    calendar_date as day,
    charged_value as body_battery_max,
    drained_value as body_battery_min
from {{ source('raw', 'body_battery') }}
