-- dbt/models/staging/stg_weather_data.sql

with source as (
    select * from {{ source('weather_source', 'raw_weather_data') }}
),

rn_cte as (
    select 
        *,
        row_number() over(
            partition by local_time 
            order by _ingested_at asc
        ) as rn
    from source
)

select 
    id,
    city,
    temp,
    weather_desc,
    windspeed,
    local_time,
    (_ingested_at + (utc_offset || 'hours')::interval) as _ingested_at_local
from rn_cte 
where rn = 1