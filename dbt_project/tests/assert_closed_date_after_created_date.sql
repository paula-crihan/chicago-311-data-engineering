select *
from {{ ref('fct_service_requests') }}
where closed_date is not null
  and closed_date < created_date