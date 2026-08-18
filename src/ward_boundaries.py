import requests
from src.config import (CURRENT_WARDS_API_URL, OLD_WARDS_API_URL )
import json
import duckdb

def fetch_current_ward_boundaries():

    response = requests.get(CURRENT_WARDS_API_URL)

    response.raise_for_status()

    data = response.json()

    print(f"Fetched {len(data)} current ward boundaries")

    return data

def load_current_ward_boundaries():

    data = fetch_current_ward_boundaries()
    con = duckdb.connect("warehouse.duckdb")

    con.execute("""
        CREATE OR REPLACE TABLE ward_boundaries_current (
            ward INTEGER,
            geometry_json VARCHAR
        )
    """)

    rows = []

    for record in data:
        ward = int(record["ward"])
        geometry_json = json.dumps(record["the_geom"])

        rows.append((ward, geometry_json))

    con.executemany(
        """
        INSERT INTO ward_boundaries_current
        VALUES (?, ?)
        """,
        rows
    )

    con.close()

    print(f"Loaded {len(rows)} current ward boundaries")

def fetch_old_ward_boundaries():

    response = requests.get(OLD_WARDS_API_URL)

    response.raise_for_status()

    data = response.json()

    print(f"Fetched {len(data)} old ward boundaries")

    return data

def load_old_ward_boundaries():

    data = fetch_old_ward_boundaries()

    con = duckdb.connect("warehouse.duckdb")

    con.execute("""
        CREATE OR REPLACE TABLE ward_boundaries_old (
            ward INTEGER,
            geometry_json VARCHAR
        )
    """)

    rows = []

    for record in data:
        ward = int(record["ward"])
        geometry_json = json.dumps(record["the_geom"])

        rows.append((ward, geometry_json))

    con.executemany(
        """
        INSERT INTO ward_boundaries_old
        VALUES (?, ?)
        """,
        rows
    )

    con.close()

    print(f"Loaded {len(rows)} old ward boundaries")