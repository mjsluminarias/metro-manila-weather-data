import sys
import os
from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
# from airflow.providers.standard.operators.latest_only import LatestOnlyOperator

# --- SYSTEM INITIALIZATION ---
# Ensures the Airflow worker can resolve custom modules from the root repository path.
root_path = os.path.abspath("/opt/airflow")
if root_path not in sys.path:
    sys.path.insert(0, root_path)

# --- MODULE INGESTION ---
# Safely imports the ingestion logic to prevent DAG parsing failures if dependencies are missing.
try:    
    from api_request.ingest_raw import main as run_weather_ingestion
except ImportError as e:
    run_weather_ingestion = None
    print(f"Import Error: {e}")

# --- RESILIENCE & BACKOFF STRATEGY ---
# Configures intelligent retries to handle transient network issues and API rate limits (HTTP 429).
default_arguments = {    
    'owner': 'aamir',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True, # Progressively waits longer between retries to respect API quotas.
    'max_retry_delay': timedelta(hours=1),
}
    
# --- PIPELINE CONFIGURATION ---
@dag(
    dag_id='weather-api-pl-orchestrator',
    schedule=None,                         # Manual trigger enabled.
    # schedule="0 */3 * * 1-5",            # Standard CRON for Mon-Fri production cadence.
    max_active_runs=1,                     # Singleton Pattern: Prevents overlapping DAG executions.
    start_date=datetime(2026, 5, 16),
    catchup=False,                         # Freshness Policy: Skips missed historical runs to avoid backlog.
    tags=['weather_platform'],
    default_args=default_arguments
)
def weather_pipeline():
       
    # --- STEP 1: RAW INGESTION (PYTHON) ---
    # Executes the API-to-Postgres ingestion logic.
    @task(
        task_id="ingest_weather_data",
        max_active_tis_per_dag=1           # Resource Lock: Ensures only one ingestion process hits the API.
    )
    def trigger_ingestion():         
        if run_weather_ingestion:
            run_weather_ingestion()
        else:
            raise ImportError("Could not find the ingestion script logic.")

    # Instantiate Ingestion Task
    ingest_task = trigger_ingestion()

    # --- STEP 2: DATA TRANSFORMATION (DBT) ---
    # Triggers dbt models inside a dedicated container to decouple compute from the orchestrator.
    dbt_run_task = BashOperator(
        task_id='transform_data_task',
        bash_command='docker exec dbt_container dbt run'
    )

    # --- DEPENDENCY GRAPH ---
    # Defines the linear progression from Freshness Check -> Ingestion -> Transformation.
    ingest_task >> dbt_run_task

# --- DAG INSTANTIATION ---
weather_pipeline()