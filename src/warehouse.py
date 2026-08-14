import duckdb
from src.config import WAREHOUSE_PATH, PIPELINE_NAME


def initialize_warehouse():
    connection = duckdb.connect(WAREHOUSE_PATH)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS pipeline_control (
            pipeline_name VARCHAR PRIMARY KEY,
            last_run_date TIMESTAMP
        )
    """)

    connection.close()

    print("Warehouse initialized successfully.")

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