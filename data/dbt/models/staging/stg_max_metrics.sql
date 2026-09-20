-- Best-guess column names, see stg_activities.sql for the caveat.

select
    day,
    generic__vo2_max_value as vo2max_running,
    cycling__vo2_max_value as vo2max_cycling
from {{ source('raw', 'max_metrics') }}
