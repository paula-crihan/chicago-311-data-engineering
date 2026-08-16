
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

)

select *
from deduplicated
