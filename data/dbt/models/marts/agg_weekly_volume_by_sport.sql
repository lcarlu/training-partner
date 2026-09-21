select
    date_trunc('week', start_time)::date as week_start,
    sport,
    -- Postgres's round() only accepts numeric (not double precision), unlike DuckDB's more
    -- permissive overload resolution - cast in, then back out to double precision so the
    -- app gets a plain float (not a decimal.Decimal) like it did on DuckDB.
    round((sum(distance_m) / 1000.0)::numeric, 1)::double precision as total_distance_km,
    round((sum(duration_s) / 3600.0)::numeric, 1)::double precision as total_duration_h,
    count(*) as activity_count
from {{ ref('fct_activities') }}
group by 1, 2
