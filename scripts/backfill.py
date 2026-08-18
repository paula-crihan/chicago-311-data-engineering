from datetime import datetime

from src.api_client import fetch_service_requests
from src.parquet_writer import save_to_parquet
from src.warehouse import load_parquet_to_warehouse
from dateutil.relativedelta import relativedelta


def backfill_period(start_date, end_date):
    print(
        f"Starting backfill from {start_date} to {end_date}"
    )

    data = fetch_service_requests(
        last_run_date=start_date,
        end_date=end_date,
        batch_size=1000
    )

    print(f"Extracted {len(data)} historical records")

    if not data:
        print("No historical records found")
        return

    file_name = (
        f"chicago_311_"
        f"{start_date.strftime('%Y%m%d')}_"
        f"{end_date.strftime('%Y%m%d')}.parquet"
    )

    file_path = save_to_parquet(
        data,
        file_name
    )

    load_parquet_to_warehouse(file_path)

    print("Backfill period completed successfully")



if __name__ == "__main__":
    # A doua jumătate din 2025
    start_date = datetime(2025, 7, 1)
    end_date = datetime(2026, 1, 1)
    backfill_period(start_date, end_date)