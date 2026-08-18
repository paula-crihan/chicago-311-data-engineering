with relevant_requests as (

    select
        community_area,
        sr_type,
        created_date,
        closed_date
    from {{ ref('fct_service_requests') }}
    where closed_date is not null
      and sr_type in (
          'Pothole in Street Complaint',
          'Graffiti Removal Request'
      )
      and year(created_date) between 2022 and 2025
      and community_area is not null

), resolution_times as (

    select
        community_area,
        sr_type,
        year(created_date) as request_year,
        date_diff('day', created_date, closed_date) as resolution_days
    from relevant_requests

), median_resolution as (

    select
        community_area,
        sr_type,
        request_year,
        median(resolution_days) as median_resolution_days
    from resolution_times
    group by
        community_area,
        sr_type,
        request_year

), year_over_year as (

    select
        community_area,
        sr_type,
        request_year,
        median_resolution_days,

        lag(median_resolution_days) over (
            partition by community_area, sr_type
            order by request_year
        ) as previous_year_median

    from median_resolution

), ranked as (

    select
        *,
        row_number() over (
            partition by request_year, sr_type
            order by median_resolution_days desc
        ) as slowest_rank

    from year_over_year

)


select
    community_area,
    sr_type,
    request_year,
    median_resolution_days,
    previous_year_median,

    case
        when previous_year_median is null then 'No previous year'
        when median_resolution_days < previous_year_median then 'Improved'
        when median_resolution_days > previous_year_median then 'Worsened'
        else 'No change'
    end as year_over_year_change

from ranked

where slowest_rank <= 5

order by
    request_year desc,
    sr_type,
    slowest_rank