# WeatherStack Data Platform: Orchestrated Medallion Pipeline

### Airflow 3.0 | dbt-Postgres | Docker | Medallion Architecture (ELT) | Resilient Ingestion

This project implements a self-healing, orchestrated data pipeline that ingests real-time weather data into a local Medallion Architecture. It leverages **Docker** for service isolation and **Airflow 3.0** for sophisticated orchestration, ensuring high data freshness while strictly adhering to API rate limits.

---

## 🛠️ Tech Stack

* **Orchestration:** Airflow 3.0 (Standalone Mode)
* **Transformation:** dbt-Core (v1.8.2) with PostgreSQL adapter
* **Database:** PostgreSQL 14 (Dockerized)
* **Ingestion:** Python (Requests, Psycopg2, YAML)
* **Environment:** Docker Compose, Python Virtual Environments (venv)
* **API:** Weatherstack REST API

---

## 🏗️ Data Architecture (Medallion)

The pipeline follows a decoupled logic where ingestion and transformation live in separate containers, coordinated by Airflow.

### Bronze Layer (Raw Ingestion)
* **Source:** Real-time JSON payload from Weatherstack API.
* **Resilience:** Implements **Exponential Backoff** to handle `HTTP 429` (Rate Limit) errors gracefully.
* **Strategy:** Stateless ingestion—only the most recent weather observation is preserved during system backlogs to ensure data utility and minimize API costs.

### Silver Layer (Cleansed & Conformed)
* **Logic:** Managed via dbt. Performs type casting, timestamp normalization (UTC to Local), and schema enforcement.
* **Quality:** Filters out null or malformed API responses.

### Gold Layer (Analytical Marts)
* **Logic:** Aggregated views providing business-ready weather metrics (e.g., daily temperature trends, wind-speed analysis).
* **Consumption:** Ready for BI tools or downstream analytical modeling.

---

## 📂 Project Structure

```text
weatherstack-platform/
├── api_request/            # Python Ingestion Logic
│   ├── ingest_raw.py       # DB Connection & Data Loading
│   └── weather_api.py      # API Client & Path Resolution
├── airflow/                # Orchestration Layer
│   └── dags/
│       └── orchestrator.py # DAG Definition (Resilience & Scheduling)
├── dbt/                    # Transformation Layer
│   ├── models/             # Medallion SQL Models (Silver/Gold)
│   └── profiles.yml        # DB Connection Profiles
├── docker-compose.yaml     # Multi-service Infrastructure
└── config.yaml             # API & Environment Configuration
```
---
## ⚙️ Orchestration & Resilience

The pipeline is designed for high reliability and API cost-efficiency using a **Senior-grade resilience strategy**:

### 1. Freshness & Concurrency Control
* **Zero Backlog:** Configured with `catchup=False` to skip stale historical runs. The platform only ever processes the most current weather data.
* **Singleton Lock:** Hard-locked to `max_active_runs=1` to prevent overlapping executions and race conditions in the target database.

### 2. Intelligent API Handling (HTTP 429)
* **Exponential Backoff:** Automatically handles rate limits by doubling the wait time between retries ($5, 10, 20...$ mins). This ensures self-healing recovery from `429 Too Many Requests` errors without manual intervention.

### 3. Decoupled Architecture
* **Sidecar Execution:** Uses Airflow strictly as a **Control Plane**, offloading heavy SQL compute to a dedicated **dbt container** via Docker-out-of-Docker execution. This protects the orchestrator's stability during large transformations.

---

## 🛡️ Security & Environment Management

The platform adheres to production-grade security standards and flexible environment routing:

* **Network Isolation:** All services are isolated within a private **Docker bridge network** (`my-network`). This ensures the database is not exposed to the public internet, allowing only internal containers to communicate.
* **Secret Management:** Sensitive credentials—including API keys and database passwords—are externalized via **.env files**. This prevents "secret leakage" by ensuring no plain-text credentials exist in the source code.
* **Dynamic Environment Routing:** The ingestion logic features **Auto-Detection** capabilities. It identifies if it is running inside a Docker container (Airflow) or a local shell (venv), automatically routing traffic to the appropriate endpoint:
  * **Production (Docker):** `db:5432`
  * **Development (Local):** `localhost:5000`
