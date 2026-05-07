"""
Airflow DAG: TheLook Ecommerce Pipeline
Runs daily at 6am: ingest CSVs → dbt run → dbt test
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule
import logging

log = logging.getLogger(__name__)

PROJECT_DIR = "/Users/mridulakalaiselvan/Desktop/thelook-pipeline"
PYTHON      = f"{PROJECT_DIR}/venv/bin/python"
DBT         = f"{PROJECT_DIR}/venv/bin/dbt"

default_args = {
    "owner": "mridula",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}

with DAG(
    dag_id="thelook_ecommerce_pipeline",
    default_args=default_args,
    description="Daily TheLook ELT pipeline: ingest → dbt run → dbt test",
    schedule_interval="0 6 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["ecommerce", "dbt", "thelook"],
) as dag:

    ingest = BashOperator(
        task_id="ingest_csvs",
        bash_command=f"{PYTHON} {PROJECT_DIR}/ingestion/ingest_thelook.py",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {PROJECT_DIR}/dbt_project && {DBT} run --profiles-dir . --select staging intermediate marts",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {PROJECT_DIR}/dbt_project && {DBT} test --profiles-dir .",
    )

    dbt_docs = BashOperator(
        task_id="dbt_docs_generate",
        bash_command=f"cd {PROJECT_DIR}/dbt_project && {DBT} docs generate --profiles-dir .",
    )

    def failure_alert(**context):
        log.error(f"Pipeline failed at task: {context['task_instance'].task_id}")

    alert = PythonOperator(
        task_id="failure_alert",
        python_callable=failure_alert,
        trigger_rule=TriggerRule.ONE_FAILED,
    )

    ingest >> dbt_run >> dbt_test >> dbt_docs
    [ingest, dbt_run, dbt_test] >> alert
