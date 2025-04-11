"""
Airflow DAG for Pet Adoption ETL Process
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import sys
import os

# Add parent directory to path to import ETL modules
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from etl.extract_csv import extract_pet_data
from etl.transform_data import clean_pet_data
from etl.load_to_db import load_to_postgres

# Sample CSV URL - replace with your actual data source
SAMPLE_PET_DATA_URL = "https://github.com/Ravinnoel09/PetAdaption_Airflow/blob/main/sample_data/pets_legacy.csv"

# Define default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create DAG
dag = DAG(
    'pet_adoption_etl',
    default_args=default_args,
    description='ETL process for pet adoption data',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2025, 4, 1),
    catchup=False,
    tags=['pet_adoption', 'etl'],
)

# Define tasks
def extract_task(**kwargs):
    """Extract pet data from source"""
    return extract_pet_data(SAMPLE_PET_DATA_URL).to_dict()

def transform_task(**kwargs):
    """Transform and clean pet data"""
    ti = kwargs['ti']
    raw_data = ti.xcom_pull(task_ids='extract_pet_data')
    df = pd.DataFrame(raw_data)
    return clean_pet_data(df).to_dict()

def load_task(**kwargs):
    """Load data to database"""
    ti = kwargs['ti']
    transformed_data = ti.xcom_pull(task_ids='transform_pet_data')
    df = pd.DataFrame(transformed_data)
    
    # Use DATABASE_URL environment variable
    return load_to_postgres(df, 'pet_data')

# Create tasks
extract = PythonOperator(
    task_id='extract_pet_data',
    python_callable=extract_task,
    dag=dag,
)

transform = PythonOperator(
    task_id='transform_pet_data',
    python_callable=transform_task,
    dag=dag,
)

load = PythonOperator(
    task_id='load_pet_data',
    python_callable=load_task,
    dag=dag,
)

# Set task dependencies
extract >> transform >> load
