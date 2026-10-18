-- dbt/models/mart/weather_report.sql

with staging as (
    select * from {{ ref('stg_weather_data') }}
),

final_mart as (
    select        
        city,
        temp,
        weather_desc,
        windspeed,
        local_time,        
        local_time::date as _date,
        case 
            when temp > 30 then 'High'
            when temp > 15 then 'Moderate'
            else 'Low'
        end as category
    from staging
)

select * from final_mart