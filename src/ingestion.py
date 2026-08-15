from datetime import datetime, timedelta
from src.api_client import fetch_service_requests
from src.parquet_writer import save_to_parquet
from src.warehouse import (
    get_last_run_date,
    load_parquet_to_warehouse,
    update_last_run_date
)
# coordoneaza procesul

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

# extragem datele noi, cu fetch limit+paginare/offset
def extract_data(batch_size=1000, max_batches=None):
    start_date = get_extraction_start_date()

    data = fetch_service_requests(
        last_run_date=start_date,
        batch_size=batch_size,
        max_batches=max_batches
    )

    print(f"Extracted {len(data)} records from the Chicago 311 API.")

    return data


# coordoneaza functiile
# def run_ingestion():
#
#     data = extract_data()

def run_ingestion(test_mode=False):
    if test_mode:
        data = extract_data(
            batch_size=3,
            max_batches=2
        )
    else:
        data = extract_data()

    if not data:
        print("No new records found.")
        return

    file_path = save_to_parquet(
        data,
        "chicago_311.parquet"
    )

    load_parquet_to_warehouse(file_path)

    # max pt ca vreau cea mai recenta data
    new_last_run_date_string = max(
        record["created_date"]
        for record in data
    )

    new_last_run_date = datetime.fromisoformat(
        new_last_run_date_string
    )

    # update_last_run_date(new_last_run_date)

    if not test_mode:
        update_last_run_date(new_last_run_date)
    else:
        print("Test mode: watermark was not updated.")

    print("Ingestion completed successfully.")

