from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import json
import os

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def mock_fetch_news():
    """Mock-fetch financial news data for AAPL and MSFT."""
    mock_data = [
        {
            "ticker": "AAPL",
            "headline": "Apple announces new AI features for upcoming iPhone",
            "timestamp": datetime.now().isoformat(),
            "content": "Apple is expected to integrate advanced generative AI into its next generation of devices, potentially boosting sales."
        },
        {
            "ticker": "MSFT",
            "headline": "Microsoft Azure sees record growth in cloud revenue",
            "timestamp": datetime.now().isoformat(),
            "content": "Strong demand for cloud services and AI infrastructure drives Microsoft's quarterly earnings beyond expectations."
        },
        {
            "ticker": "AAPL",
            "headline": "Supply chain issues might affect iPhone production",
            "timestamp": datetime.now().isoformat(),
            "content": "Reports suggest that components for high-end iPhone models are facing delays in several key regions."
        }
    ]
    
    staging_dir = '/workspaces/Real-Time-Market-Sentiment-Volatility-Orchestrator/data'
    os.makedirs(staging_dir, exist_ok=True)
    file_path = os.path.join(staging_dir, 'staged_news.json')
    
    with open(file_path, 'w') as f:
        json.dump(mock_data, f, indent=4)
    
    print(f"Staged {len(mock_data)} news items to {file_path}")

with DAG(
    'market_data_pipeline',
    default_args=default_args,
    description='A DAG to ingest market news and process sentiment',
    schedule_interval=timedelta(days=1),
    catchup=False,
) as dag:

    fetch_news_task = PythonOperator(
        task_id='fetch_news',
        python_callable=mock_fetch_news,
    )

    def run_process_sentiment():
        import subprocess
        subprocess.run(["python3", "/workspaces/Real-Time-Market-Sentiment-Volatility-Orchestrator/scripts/process_sentiment.py"], check=True)

    process_sentiment_task = PythonOperator(
        task_id='process_sentiment',
        python_callable=run_process_sentiment,
    )

    def ingest_data():
        import requests
        import json
        processed_file = '/workspaces/Real-Time-Market-Sentiment-Volatility-Orchestrator/data/processed_news.json'
        if os.path.exists(processed_file):
            # In a real setup, the Flask app URL would be configurable
            url = 'http://localhost:5000/ingest'
            with open(processed_file, 'r') as f:
                data = json.load(f)
                response = requests.post(url, json=data)
                response.raise_for_status()
                print(f"Successfully ingested data: {response.status_code}")
        else:
            print("No processed data found to ingest.")

    ingest_task = PythonOperator(
        task_id='ingest_to_clickhouse',
        python_callable=ingest_data,
    )

    fetch_news_task >> process_sentiment_task >> ingest_task
