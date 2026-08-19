from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    "owner": "airflow"
}

with DAG(
    dag_id="production_pipeline",
    default_args=default_args,
    start_date=datetime(2026,1,1),
    schedule=None,
    catchup=False,
    tags=["Exercise5"],
) as dag:

    consumer = BashOperator(
        task_id="youtube_consumer",
        bash_command="cd /opt/airflow/scripts && python youtube_consumer.py"
    )

    validation = BashOperator(
        task_id="validate_data",
        bash_command="cd /opt/airflow/scripts && python validate_data.py"
    )

    merge = BashOperator(
        task_id="idempotent_merge",
        bash_command="cd /opt/airflow/scripts && python idempotent_merge.py"
    )

    sqlite = BashOperator(
        task_id="load_sqlite",
        bash_command="cd /opt/airflow/scripts && python load_sqlite.py"
    )

    consumer >> validation >> merge >> sqlite