with wards as (

    select distinct ward
    from {{ ref('stg_service_requests') }}
    where ward is not null

),

boundary_change as (

    select
        cast(effective_from as date) as change_date
    from {{ ref('ward_boundary_changes') }}
    where boundary_version = 'current'

), ward_versions as (

select
    concat(cast(w.ward as varchar), '-', 'old') as ward_version_key,
    w.ward,
    'old' as boundary_version,
    null::date as valid_from,
    b.change_date as valid_to
    from wards w
    cross join boundary_change b

    union all

   select
    concat(cast(w.ward as varchar), '-', 'current') as ward_version_key,
    w.ward,
    'current' as boundary_version,
    b.change_date as valid_from,
    null::date as valid_to

    from wards w
    cross join boundary_change b

)

select *
from ward_versions