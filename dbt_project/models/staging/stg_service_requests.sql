select
    trim(sr_number) as sr_number,
    trim(owner_department) as owner_department,
    trim(origin) as origin,
    trim(created_department) as created_department,
    trim(street_address) as street_address,
    trim(street_number) as street_number,
    trim(street_direction) as street_direction,
    trim(street_name) as street_name,
    trim(street_type) as street_type,
    trim(city) as city,
    trim(state) as state,
    trim(zip_code) as zip_code,
    trim(electricity_grid) as electricity_grid,

--   convert from varchar in time/integer/douuble
    try_cast(trim(created_date) as timestamp) as created_date,
    try_cast(trim(last_modified_date) as timestamp) as last_modified_date,
    try_cast(trim(closed_date) as timestamp) as closed_date,

    try_cast(trim(community_area) as integer) as community_area,
    try_cast(trim(ward) as integer) as ward,
    try_cast(trim(created_hour) as integer) as created_hour,
    try_cast(trim(created_day_of_week) as integer) as created_day_of_week,
    try_cast(trim(created_month) as integer) as created_month,

    try_cast(trim(latitude) as double) as latitude,
    try_cast(trim(longitude) as double) as longitude,

    try_cast(trim(electrical_district) as integer) as electrical_district,
    try_cast(trim(police_sector) as integer) as police_sector,
    try_cast(trim(police_district) as integer) as police_district,
    try_cast(trim(police_beat) as integer) as police_beat,
    try_cast(trim(precinct) as integer) as precinct,

    try_cast(trim(x_coordinate) as double) as x_coordinate,
    try_cast(trim(y_coordinate) as double) as y_coordinate,

    duplicate,
    legacy_record,
    trim(parent_sr_number) as parent_sr_number,
    location,

--    normalize inconsistent text fields (sr_type, sr_short_code, status)
    case
    when lower(trim(status)) = 'open' then 'Open'
    when lower(trim(status)) = 'completed' then 'Completed'
    when lower(trim(status)) = 'canceled' then 'Canceled'
    else trim(status)
    end as status,

    trim(sr_type) as sr_type,
    upper(trim(sr_short_code)) as sr_short_code,

from {{ source('raw', 'raw_service_requests') }}