# Real-Time Market Sentiment & Volatility Orchestrator

This project automates financial news ingestion, analyzes sentiment and volatility drivers using the Gemini CLI, stores results in ClickHouse, and visualizes them on a React dashboard.

## Prerequisites
- Python 3.9+
- Apache Airflow
- ClickHouse (running locally on port 8123)
- Node.js & npm
- [Gemini CLI](https://github.com/google/gemini-cli) (authenticated and in PATH)

## Phase 1 & 2: Airflow Pipeline & AI Processing
1. **Initialize Airflow**:
   ```bash
   export AIRFLOW_HOME=$(pwd)/airflow
   airflow db init
   airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com
   ```
2. **Deploy DAG**:
   The DAG is located in `./dags/market_data_pipeline.py`. Ensure your `airflow.cfg` points to this directory or copy the DAG to your `AIRFLOW_HOME/dags`.
3. **Start Airflow**:
   ```bash
   airflow scheduler &
   airflow webserver -p 8080 &
   ```

## Phase 3: Database & Backend
1. **Initialize ClickHouse**:
   Run the DDL command found in `backend/schema.sql`:
   ```bash
   clickhouse-client --queries-file backend/schema.sql
   ```
2. **Start Flask Server**:
   ```bash
   cd backend
   pip install flask flask-cors clickhouse-connect requests
   python3 app.py
   ```

## Phase 4: Frontend Dashboard
1. **Setup React**:
   (Assuming a standard Vite/React setup)
   ```bash
   cd frontend
   npm install
   npm install -D tailwindcss postcss autoprefixer
   npx tailwindcss init -p
   # Ensure your tailwind.config.js and index.css are configured for Phase 4 code.
   npm run dev
   ```

## Workflow Summary
- **Airflow DAG**: `fetch_news` -> `process_sentiment` (Calls Gemini CLI) -> `ingest_to_clickhouse` (Hits Flask `/ingest`).
- **Flask Backend**: Exposes `/ingest` for Airflow and `/api/sentiment/<ticker>` for the Dashboard.
- **React Dashboard**: Fetches data from Flask and displays sentiment scores and volatility drivers.

## Error Handling
The `process_sentiment.py` script includes robust error handling for subprocess calls to the Gemini CLI, capturing stderr and handling JSON parsing issues gracefully.
