select
    date_trunc('week', start_time)::date as week_start,
    sport,
    round(sum(distance_m) / 1000.0, 1) as total_distance_km,
    round(sum(duration_s) / 3600.0, 1) as total_duration_h,
    count(*) as activity_count
from {{ ref('fct_activities') }}
group by 1, 2
