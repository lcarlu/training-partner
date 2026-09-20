-- Best-guess column names, see stg_activities.sql for the caveat.

select
    day,
    score as training_readiness_score
from {{ source('raw', 'training_readiness') }}
