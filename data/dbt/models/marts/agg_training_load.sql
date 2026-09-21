-- Forward-looking mart, not yet consumed by the API: a day-by-day training readiness/status
-- timeline, ready for a future "load over time" chart without recomputing anything Garmin-side.

select
    day,
    training_readiness_score,
    training_status
from {{ ref('fct_daily_wellness') }}
order by day
