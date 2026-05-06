# Project Issues & Resolutions Log

This document tracks technical hurdles encountered during the setup and execution of the Real-Time Market Sentiment & Volatility Orchestrator.

## 1. Airflow Metadata Database Corruption
- **Problem:** `airflow db init` failed with `alembic.util.exc.CommandError: Can't locate revision identified by '22ed7efa9da2'`. This indicated an incompatible or corrupted SQLite database file.
- **Resolution:** Deleted the existing `airflow/airflow.db` and re-initialized the database from scratch.

## 2. Missing ClickHouse Infrastructure
- **Problem:** The system lacked the ClickHouse server required for data storage. `clickhouse-client` was not found, and port `8123` was closed.
- **Resolution:** Deployed ClickHouse using Docker:
  ```bash
  docker run -d --name clickhouse-server -p 8123:8123 -p 9000:9000 clickhouse/clickhouse-server:latest
  ```

## 3. ClickHouse Authentication Failures
- **Problem:** The Flask backend initially failed to connect to ClickHouse with a `DatabaseError: Authentication failed`.
- **Resolution:** Reset the ClickHouse container without conflicting environment variables to allow the default "no-password" access for the `default` user, and successfully initialized the schema.

## 4. Frontend Accessibility ("Failed to Fetch")
- **Problem:** The Vite dev server was listening on `localhost:5173`, making it inaccessible. Additionally, the dashboard was reporting "Failed to fetch" because the backend (port 5000) was not consistently reachable or running.
- **Resolution:** 
  - Updated `frontend/vite.config.js` to set `server.host: '0.0.0.0'`.
  - Verified Flask CORS settings in `backend/app.py`.
  - Restarted both services using `nohup` to ensure persistence.

## 5. Airflow Scheduler Task Failures
- **Problem:** Tasks were being marked as `failed` immediately after being `queued`. Logs showed: `Executor reports task instance ... finished (failed) although the task says it's queued`.
- **Resolution:** Killed all orphan Airflow processes, removed stale `.pid` files in the `airflow/` directory, and restarted the scheduler.

## 6. Backend Ingestion 500 Errors
- **Problem:** The Airflow `ingest_to_clickhouse` task received a 500 error from the Flask backend.
- **Root Cause:** The backend was unable to connect to ClickHouse due to authentication failures.
- **Resolution:** 
  - Restarted ClickHouse with explicit credentials (`default` / `password`).
  - Hardcoded the fallback password in `backend/app.py` to ensure reliable connectivity.
  - Verified connection with a manual `curl` test.
