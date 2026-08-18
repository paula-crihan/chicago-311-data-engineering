with requests_with_location as (

    select
        sr_number,
        created_date,
        ward as recorded_ward,
        latitude,
        longitude
    from {{ ref('fct_service_requests') }}
    where latitude is not null
      and longitude is not null
      and year(created_date) between 2022 and 2024

), current_map_assignment as (

    select
        r.sr_number,
        r.created_date,
        r.recorded_ward,
        current_w.ward as current_ward

    from requests_with_location r

    left join ward_boundaries_current current_w
        on ST_Contains(
            ST_GeomFromGeoJSON(current_w.geometry_json),
            ST_Point(r.longitude, r.latitude)
        )

), historical_volumes_requests as (

    select
        year(created_date) as request_year,
        recorded_ward as ward,
        count(*) as historical_request_volume
    from current_map_assignment
    where recorded_ward is not null
    group by
        request_year,
        recorded_ward

), current_map_volumes_requests as (

    select
        year(created_date) as request_year,
        current_ward as ward,
        count(*) as current_map_request_volume
    from current_map_assignment
    where current_ward is not null
    group by
        request_year,
        current_ward

), volume_comparison as (

    select
        h.request_year,
        h.ward,
        h.historical_request_volume,
        c.current_map_request_volume,

        c.current_map_request_volume
            - h.historical_request_volume as volume_difference,

        round(
            (
                c.current_map_request_volume
                - h.historical_request_volume
            ) * 100.0 / h.historical_request_volume,
            2
        ) as volume_difference_percent

    from historical_volumes_requests h

    left join current_map_volumes_requests c
        on h.request_year = c.request_year
        and h.ward = c.ward

)

select
    request_year,
    ward,
    historical_request_volume,
    current_map_request_volume,
    volume_difference,
    volume_difference_percent
from volume_comparison

order by
    request_year,
    abs(volume_difference_percent) desc