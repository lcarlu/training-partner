-- Best-guess column names, see stg_activities.sql for the caveat.

select
    day,
    most_recent_training_status__latest_training_status_data__status as training_status
from {{ source('raw', 'training_status') }}
