#!/bin/bash

# Ensure script fails on any error
set -e

echo "📦 Setting up Airflow environment..."
export AIRFLOW_HOME=${AIRFLOW_HOME:-$(pwd)/airflow}
mkdir -p $AIRFLOW_HOME

# Set default database path if not provided
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=${AIRFLOW__DATABASE__SQL_ALCHEMY_CONN:-sqlite:///$AIRFLOW_HOME/airflow.db}

# Set default DAGs folder
export AIRFLOW__CORE__DAGS_FOLDER=${AIRFLOW__CORE__DAGS_FOLDER:-$(pwd)/airflow_dags}

echo "📦 Initializing Airflow DB..."
airflow db init

echo "🔐 Creating Airflow user..."
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin || true

echo "🚀 Starting Airflow scheduler in standalone mode..."
exec airflow scheduler
