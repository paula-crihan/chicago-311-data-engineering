FROM apache/airflow:2.11.2

RUN pip install --no-cache-dir \
    requests \
    pyarrow \
    duckdb \
    dbt-duckdb