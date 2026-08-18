import os


API_URL = "https://data.cityofchicago.org/resource/v6vf-nfxy.json"

PIPELINE_NAME = "chicago_311"

BASE_PATH = os.getenv("PROJECT_ROOT", ".")

WAREHOUSE_PATH = os.path.join(
    BASE_PATH,
    "warehouse.duckdb"
)

RAW_DATA_PATH = os.path.join(
    BASE_PATH,
    "raw"
)

CURRENT_WARDS_API_URL = (
    "https://data.cityofchicago.org/resource/p293-wvbd.json"
)

OLD_WARDS_API_URL = (
    "https://data.cityofchicago.org/resource/k9yb-bpqx.json"
)