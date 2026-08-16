select *
from {{ ref('fct_service_requests') }}
where ward is not null
  and ward_version_key is null