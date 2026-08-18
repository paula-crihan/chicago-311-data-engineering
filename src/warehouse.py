import duckdb
from src.config import WAREHOUSE_PATH, PIPELINE_NAME

# duckdb

# creeaza pipeline_control
def initialize_warehouse():
    connection = duckdb.connect(WAREHOUSE_PATH)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS pipeline_control (
            pipeline_name VARCHAR PRIMARY KEY,
            last_run_date TIMESTAMP
        )
    """)

    connection.close()

    print("Warehouse initialized successfully")

def get_last_run_date():
    connection = duckdb.connect(WAREHOUSE_PATH)

    result = connection.execute("""
        SELECT last_run_date
        FROM pipeline_control
        WHERE pipeline_name = ?
    """, [PIPELINE_NAME]).fetchone()

    connection.close()

    if result is None:
        return None

    return result[0]

def load_parquet_to_warehouse(file_path):
    connection = duckdb.connect(WAREHOUSE_PATH)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS raw_service_requests AS
        SELECT *
        FROM read_parquet(?)
        LIMIT 0
    """, [file_path])

    connection.execute("""
        INSERT INTO raw_service_requests BY NAME
        SELECT p.*
        FROM read_parquet(?) AS p
        WHERE NOT EXISTS (
            SELECT 1
            FROM raw_service_requests AS r
            WHERE r.sr_number = p.sr_number
              AND r.last_modified_date = p.last_modified_date
        )
    """, [file_path])

    connection.close()

    print(f"Loaded Parquet data into DuckDB from {file_path}")


def update_last_run_date(last_run_date):
    connection = duckdb.connect(WAREHOUSE_PATH)

    connection.execute("""
        INSERT INTO pipeline_control (
            pipeline_name,
            last_run_date
        )
        VALUES (?, ?)
        ON CONFLICT (pipeline_name)
        DO UPDATE SET
            last_run_date = EXCLUDED.last_run_date
    """, [PIPELINE_NAME, last_run_date])

    connection.close()

    print(f"Watermark updated to: {last_run_date}")