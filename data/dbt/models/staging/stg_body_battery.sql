-- `body_battery_min`/`body_battery_max` are precomputed in the dlt resource (from the raw
-- `bodyBatteryValuesArray` samples) since there's no ready-made min/max field on this endpoint.

select
    date::date as day,
    body_battery_min,
    body_battery_max
from {{ source('raw', 'body_battery') }}
