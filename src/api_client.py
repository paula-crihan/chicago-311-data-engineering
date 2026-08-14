import requests

from src.config import API_URL

#
# def fetch_service_requests(last_run_date, batch_size=1000):
#     formatted_date = last_run_date.strftime("%Y-%m-%dT%H:%M:%S")
#
#     all_data = []
#     offset = 0
#
#     while True:
#         params = {
#             "$where": f"created_date > '{formatted_date}'",
#             "$order": "created_date ASC, sr_number ASC",
#             "$limit": batch_size,
#             "$offset": offset
#         }
#
#         response = requests.get(API_URL, params=params)
#         response.raise_for_status()
#
#         batch = response.json()
#
#         all_data.extend(batch)
#
#         print(f"Fetched {len(batch)} records at offset {offset}.")
#
#         if len(batch) < batch_size:
#             break
#
#         offset += batch_size
#
#     return all_data


def fetch_service_requests(last_run_date, batch_size=1000, max_batches=None):
    formatted_date = last_run_date.strftime("%Y-%m-%dT%H:%M:%S")

    all_data = []
    offset = 0
    batch_number = 0

    while True:
        params = {
            "$where": f"created_date > '{formatted_date}'",
            "$order": "created_date ASC, sr_number ASC",
            "$limit": batch_size,
            "$offset": offset
        }

        response = requests.get(API_URL, params=params)
        response.raise_for_status()

        batch = response.json()

        all_data.extend(batch)
        batch_number += 1

        print(f"Fetched {len(batch)} records at offset {offset}.")

        if len(batch) < batch_size:
            break

        if max_batches is not None and batch_number >= max_batches:
            print("Maximum number of test batches reached.")
            break

        offset += batch_size

    return all_data