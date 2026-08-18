import requests
from src.config import API_URL
from airflow.hooks.base import BaseHook
import time
# comunicare cu chicago 311 api

def get_socrata_headers():
    connection = BaseHook.get_connection("socrata_chicago")

    app_token = connection.extra_dejson.get("app_token")

    return {
        "X-App-Token": app_token
    }

#returneaza datele primite in format json
def fetch_service_requests(last_run_date, end_date=None, batch_size=1000, max_batches=None):

    formatted_date = last_run_date.strftime("%Y-%m-%dT%H:%M:%S")
    if end_date is not None:
        formatted_end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S")

    all_data = []
    offset = 0
    batch_number = 0
    headers = get_socrata_headers()

    while True:

        if end_date is not None:
            where_clause = (
                f"created_date >= '{formatted_date}' "
                f"AND created_date < '{formatted_end_date}'"
            )
        else:
            where_clause = f"created_date > '{formatted_date}'"

        params = {
            "$where": where_clause,
            "$order": "created_date ASC, sr_number ASC",
            "$limit": batch_size,
            "$offset": offset
        }

        # response = requests.get(
        #     API_URL,
        #     params=params,
        #     headers=headers
        # )
        # response.raise_for_status()

        max_retries = 5

        for attempt in range(max_retries):
            response = requests.get(
                API_URL,
                params=params,
                headers=headers
            )

            if response.status_code in [500, 503]:
                if attempt < max_retries - 1:
                    print(
                        f"Server error {response.status_code}. "
                        f"Retrying in 10 seconds..."
                    )
                    time.sleep(10)
                    continue

            response.raise_for_status()
            break

        batch = response.json()

        all_data.extend(batch)
        batch_number += 1

        print(f"Fetched {len(batch)} records at offset {offset}.")

        if len(batch) < batch_size:
            break

        if max_batches is not None and batch_number >= max_batches:
            print("Maximum number of test batches reached")
            break

        offset += batch_size

    return all_data