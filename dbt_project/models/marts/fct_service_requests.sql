
{{
    config(
        materialized='incremental',
        unique_key='sr_number',
        incremental_strategy='merge'
    )
}}

with service_requests as (

    select *
    from {{ ref('stg_service_requests') }}

    {% if is_incremental() %}

    where last_modified_date > (
--    prima valoare care nu este nul
        select coalesce(
            max(last_modified_date),
            timestamp '1900-01-01'
        )
--        this->  model curent
        from {{ this }}
    )

{% endif %}

)

--select *
--from service_requests

, deduplicated as (

    select *
    from service_requests

    qualify row_number() over (
        partition by sr_number
        order by last_modified_date desc
    ) = 1

), with_ward_version as (

    select
        d.*,
        w.ward_version_key,
        w.boundary_version
    from deduplicated d

    left join {{ ref('dim_ward') }} w
        on d.ward = w.ward
        and (
            w.valid_from is null
            or d.created_date >= w.valid_from
        )
        and (
            w.valid_to is null
            or d.created_date < w.valid_to
        )

)

select *
from with_ward_version