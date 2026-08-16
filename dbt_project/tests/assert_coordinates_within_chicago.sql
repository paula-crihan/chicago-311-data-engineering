--lat:   41.64 → 42.03
--long: -87.95 → -87.52


{% set min_lat = 41.64 %}
{% set max_lat = 42.03 %}
{% set min_lon = -87.95 %}
{% set max_lon = -87.52 %}

select *
from {{ ref('fct_service_requests') }}
where latitude is not null
  and longitude is not null
  and (
      latitude < {{ min_lat }}
      or latitude > {{ max_lat }}
      or longitude < {{ min_lon }}
      or longitude > {{ max_lon }}
  )