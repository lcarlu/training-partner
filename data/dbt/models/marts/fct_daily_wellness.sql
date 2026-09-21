-- One row per calendar day the athlete has *any* wellness signal for, left-joining every
-- per-source staging model (each of which may miss days Garmin has no data for).
--
-- VO2max comes from stg_training_status (mostRecentVO2Max, present on every training-status
-- call) rather than stg_max_metrics (`get_max_metrics` returns an empty list on most days on
-- a live account) - stg_max_metrics is kept as a synced source but unused here for now.

with days as (
    select day from {{ ref('stg_daily_stats') }}
    union
    select day from {{ ref('stg_sleep') }}
    union
    select day from {{ ref('stg_hrv') }}
    union
    select day from {{ ref('stg_stress') }}
    union
    select day from {{ ref('stg_training_readiness') }}
    union
    select day from {{ ref('stg_training_status') }}
    union
    select day from {{ ref('stg_body_battery') }}
)

select
    d.day,
    ds.resting_hr,
    hrv.hrv_status,
    hrv.hrv_last_night_avg,
    bb.body_battery_min,
    bb.body_battery_max,
    st.stress_avg,
    sl.sleep_score,
    sl.sleep_duration_s,
    ts.vo2max_running,
    ts.vo2max_cycling,
    tr.training_readiness_score,
    ts.training_status
from days d
left join {{ ref('stg_daily_stats') }} ds using (day)
left join {{ ref('stg_sleep') }} sl using (day)
left join {{ ref('stg_hrv') }} hrv using (day)
left join {{ ref('stg_stress') }} st using (day)
left join {{ ref('stg_training_readiness') }} tr using (day)
left join {{ ref('stg_training_status') }} ts using (day)
left join {{ ref('stg_body_battery') }} bb using (day)
