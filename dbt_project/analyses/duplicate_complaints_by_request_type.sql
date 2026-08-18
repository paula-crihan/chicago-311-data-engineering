with base_requests as (

    select
        sr_number,
        sr_type,
        street_address,
        created_date,
        duplicate,
        parent_sr_number
    from {{ ref('fct_service_requests') }}
    where street_address is not null
    and sr_type is not null
    and sr_type not in (
      'Aircraft Noise Complaint',
      '311 INFORMATION ONLY CALL'
  )

), previous_requests as (

    select
        *,
        lag(created_date) over (
            partition by street_address, sr_type
            order by created_date
        ) as previous_created_date

    from base_requests

), flagged_requests as (

    select
        *,
        date_diff(
            'day',
            previous_created_date,
            created_date
        ) as days_since_previous

    from previous_requests

), classified_requests as (

    select
        *,
        case
            when previous_created_date is not null
                 and days_since_previous <= 3
            then 1
            else 0
        end as possible_duplicate

    from flagged_requests

), duplicate_ratios as (

    select
        sr_type,
        count(*) as total_requests,

        sum(
            case
                when duplicate = true then 1
                else 0
            end
        ) as official_duplicate_requests,

        round(
            100.0 * sum(
                case
                    when duplicate = true then 1
                    else 0
                end
            ) / count(*),
            2
        ) as official_duplicate_ratio_percent,

        sum(possible_duplicate) as short_window_repeat_requests,

        round(
            100.0 * sum(possible_duplicate) / count(*),
            2
        ) as short_window_repeat_ratio_percent

    from classified_requests

    group by sr_type
    having count(*) >= 1000
)

select
    sr_type,
    total_requests,
    official_duplicate_requests,
    official_duplicate_ratio_percent,
    short_window_repeat_requests,
    short_window_repeat_ratio_percent

from duplicate_ratios

--order by official_duplicate_ratio_percent desc
order by short_window_repeat_ratio_percent desc