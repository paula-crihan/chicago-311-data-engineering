import duckdb
from datetime import datetime, timedelta

connection = duckdb.connect("warehouse.duckdb")

connection.execute("""
    CREATE TABLE IF NOT EXISTS pipeline_control (
        pipeline_name VARCHAR PRIMARY KEY,
        last_run_date TIMESTAMP
    )
""")

print("The pipeline_control table was created ")

result = connection.execute("""
    SELECT last_run_date
    FROM pipeline_control
    WHERE pipeline_name = 'chicago_311'
""").fetchone()

if result is None:
    yesterday = datetime.now() - timedelta(days=1)
    last_run_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)

    print("No watermark found. Using yesterday as the initial start date:", last_run_date)
else:
    last_run_date = result[0]
    print("Watermark found:", last_run_date)

print("Query result:", result)

connection.close()