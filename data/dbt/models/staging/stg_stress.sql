-- Best-guess column names, see stg_activities.sql for the caveat.

select
    day,
    avg_stress_level as stress_avg
from {{ source('raw', 'stress') }}
