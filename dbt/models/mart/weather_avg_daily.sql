-- dbt/models/mart/weather_avg_daily.sql

select
    city,
    date(local_time) as _date,
    round(avg(temp)::numeric, 2) as avg_temp,
    round(avg(windspeed)::numeric, 2) as avg_windspeed
from {{ ref('stg_weather_data') }}    
group by 
    city,
    date(local_time)