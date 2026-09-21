select
    activity_id,
    case
        when sport_raw ilike '%run%' then 'running'
        when sport_raw ilike '%cycl%' or sport_raw ilike '%bik%' then 'cycling'
        when sport_raw ilike '%swim%' then 'swimming'
        when sport_raw ilike '%strength%' or sport_raw ilike '%training%' then 'strength'
        else 'other'
    end as sport,
    name,
    start_time,
    duration_s,
    distance_m,
    avg_hr,
    max_hr,
    calories,
    elevation_gain_m,
    training_effect_aerobic,
    training_effect_anaerobic
from {{ ref('stg_activities') }}
