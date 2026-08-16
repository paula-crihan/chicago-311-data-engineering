{% snapshot dim_ward_snapshot %}

{{
    config(
        target_schema='main',
        unique_key='ward_version_key',
        strategy='check',
        check_cols=['valid_from', 'valid_to']
    )
}}

select *
from {{ ref('dim_ward') }}

{% endsnapshot %}