{% snapshot service_requests_snapshot %}

{{
    config(
        target_schema='main',
        unique_key='sr_number',
        strategy='check',
        check_cols=['status']
    )
}}

select *
from {{ ref('fct_service_requests') }}

{% endsnapshot %}