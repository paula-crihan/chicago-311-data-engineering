from datetime import datetime, timedelta
from src.warehouse import initialize_warehouse, get_last_run_date
from src.api_client import fetch_service_requests


def get_extraction_start_date():
    last_run_date = get_last_run_date()

    if last_run_date is None:
        yesterday = datetime.now() - timedelta(days=1)

        last_run_date = yesterday.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        print("No watermark found. Using yesterday as the initial start date")

    else:
        print("Watermark found in the control table")

    return last_run_date

def extract_data(limit=1000):
    start_date = get_extraction_start_date()

    data = fetch_service_requests(
        last_run_date=start_date,
        limit=limit
    )

    print(f"Extracted {len(data)} records from the Chicago 311 API.")

    return data