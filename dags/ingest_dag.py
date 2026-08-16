from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from src.ingestion import extract_to_parquet, load_to_warehouse
from airflow.operators.bash import BashOperator


default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="chicago_311_pipeline",
    default_args=default_args,
    description="Chicago 311 end-to-end data pipeline",
    start_date=datetime(2026, 8, 1),
    schedule="@daily",
    catchup=False,
    max_active_runs=1,
    render_template_as_native_obj=True,
) as dag:

    extract = PythonOperator(
        task_id="extract",
        python_callable=extract_to_parquet
    )
    load = PythonOperator(
        task_id="load",
        python_callable=load_to_warehouse,
        op_args=["{{ ti.xcom_pull(task_ids='extract') }}"]
    )
    transform = BashOperator(
        task_id="transform",
        bash_command=(
            "cd /opt/airflow/dbt_project && "
            "dbt run --profiles-dir ."
        )
    )
    validate = BashOperator(
        task_id="validate",
        bash_command=(
            "cd /opt/airflow/dbt_project && "
            "dbt test --profiles-dir ."
        )
    )

    extract >> load >>transform>> validate
