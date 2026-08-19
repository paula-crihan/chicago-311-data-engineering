# Chicago 311 Data Engineering Project

## Project Overview

This project implements an end-to-end data engineering pipeline for Chicago 311 Service Requests.

Data is extracted incrementally from the City of Chicago Socrata API, stored as Parquet files, loaded into a DuckDB data warehouse, transformed and tested using dbt, and orchestrated using Apache Airflow.

The project maintains the current state of service requests while also preserving historical changes through dbt snapshots.

Historical data from 2022 to 2025 was backfilled to support year-over-year analysis and the study of Chicago's 2023 ward redistricting.

The project answers three analytical questions:

1. Which community areas have the slowest median resolution time for pothole and graffiti requests, and whether resolution times improved or worsened year-over-year.
2. Which request types have the highest ratio of repeated or duplicate complaints at the same location within a short time window.
3. How ward-level request volumes change when requests are attributed using the ward boundaries in effect at the time versus the current ward map.

## Architecture

The project follows an end-to-end data pipeline:

Socrata API → Apache Airflow → Parquet → DuckDB → dbt → Analytical Queries

### Pipeline Flow

1. **Extraction**  
   Chicago 311 Service Request data is extracted from the Socrata API. Incremental extraction uses a watermark (`last_run_date`) stored in DuckDB so that only new records are requested during regular pipeline runs.

2. **Raw Storage**  
   Extracted records are stored as Parquet files in the `raw/` directory before being loaded into the data warehouse.

3. **Loading**  
   Parquet data is loaded into DuckDB, which acts as the local data warehouse for the project.

4. **Transformation**  
   dbt transforms the raw data into staging and mart models. The staging layer performs cleaning, type casting, and standardization, while the marts contain query-ready data used for analysis.

5. **Historical Tracking**  
   dbt snapshots preserve historical changes in service requests and ward information.

6. **Validation**  
   dbt tests validate primary keys, relationships, geographic coordinates, dates, and other data quality rules.

7. **Orchestration**  
   Apache Airflow coordinates the pipeline through four main tasks:

   `extract → load → transform → validate`

## Project Structure

```text
chicago-311-data-engineering/
│
├── dags/
│   └── ingest_dag.py
│
├── dbt_project/
│   ├── analyses/
│   ├── models/
│   │   ├── staging/
│   │   └── marts/
│   ├── snapshots/
│   ├── tests/
│   ├── seeds/
│   └── dbt_project.yml
│
├── raw/
│
├── scripts/
│   └── backfill.py
│
├── src/
│
├── docs/
│
├── docker-compose.yml
├── warehouse.duckdb
└── README.md
```

### Folder Description

- **`dags/`** – contains the Apache Airflow DAG used to orchestrate the pipeline.
- **`dbt_project/`** – contains dbt models, analyses, snapshots, seeds, and data quality tests.
- **`raw/`** – stores extracted Chicago 311 data in Parquet format.
- **`scripts/`** – contains utility scripts used for operations such as the historical backfill.
- **`src/`** – contains the Python modules responsible for extraction, ingestion, warehouse operations, configuration, and ward boundary processing.
- **`docs/`** – contains the final project documentation.
## Technologies Used

- **Python 3.10** – data extraction, ingestion, backfill, and utility scripts.
- **Socrata API** – source of Chicago 311 Service Request data.
- **Apache Airflow** – pipeline orchestration and scheduling.
- **Docker / Docker Compose** – local Airflow environment.
- **Apache Parquet** – raw data storage format.
- **DuckDB** – local analytical data warehouse.
- **dbt (data build tool)** – data transformation, modeling, testing, snapshots, and analytical queries.
- **DuckDB Spatial Extension** – geographic processing used to compare historical and current ward boundaries.
- **Git / GitHub** – source control and project versioning.



## Setup and How to Run

### 1. Clone the Repository

Clone the project and navigate to the project directory:

```bash
git clone <repository-url>
cd chicago-311-data-engineering
```

### 2. Create the Python Environment

The project uses Python 3.10.

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install the required Python packages:

```bash
pip install requests duckdb pyarrow
```

### 3. Configure Environment Variables

Create a `.env` file in the project root.

The file is used by Docker Compose to provide environment-specific Airflow configuration, including:

```env
AIRFLOW_WEBSERVER_SECRET_KEY=YOUR_SECRET_KEY
AIRFLOW_FERNET_KEY=YOUR_FERNET_KEY
```

The `.env` file is excluded from Git so that sensitive configuration values are not committed to the repository.

The Socrata App Token is configured separately through the Airflow Connection `socrata_chicago`.

### 4. Initialize DuckDB

Initialize the local DuckDB warehouse before running the pipeline for the first time:

```bash
python init_warehouse.py
```

This creates the DuckDB warehouse and the `pipeline_control` table used to store the extraction watermark.

The watermark (`last_run_date`) allows the pipeline to perform incremental extraction by requesting only records newer than the previous successful run.

### 5. Configure and Start Apache Airflow

Apache Airflow runs locally using Docker Compose.

Start the Airflow environment from the project root:

```bash
docker compose up -d
```

After the containers are running, open the Airflow web interface in the browser.

#### Configure the Socrata Connection

The Socrata App Token used by the pipeline is stored in an Airflow Connection instead of being hard-coded in the DAG.

In the Airflow interface, go to:

`Admin → Connections`

Create the Socrata connection required by the pipeline and store the App Token in the connection configuration.

Create a connection with the following Connection ID:

`socrata_chicago`


This allows Airflow to securely provide the token to the extraction task when the DAG runs.

#### Run the Pipeline

The main Airflow DAG is:

`chicago_311_pipeline`

Trigger the DAG manually from the Airflow interface.

The pipeline executes the following tasks in order:

`extract → load → transform → validate`

- **extract** – retrieves new Chicago 311 records from the Socrata API.
- **load** – loads the extracted Parquet data into DuckDB.
- **transform** – runs the dbt transformations.
- **validate** – runs the dbt data quality tests.

### 6. Run the Historical Backfill

Historical Chicago 311 data is required for the analytical questions and year-over-year comparisons.

The project backfills historical service requests for the period 2022–2025.

Because the dataset contains several million records, the historical extraction is performed in approximately six-month intervals rather than retrieving the entire period in a single run. This reduces the amount of data processed by each execution and makes the backfill easier to manage and restart if necessary.

Run the backfill script from the project root:

```bash
docker compose exec airflow-scheduler python -m scripts.backfill
```

For each execution, configure the required start and end dates for the historical interval being processed.

The backfill process:

- extracts historical records from the Socrata API in batches;
- processes approximately six months of historical data at a time;
- writes the extracted data to Parquet files;
- loads the historical records into DuckDB;
- avoids loading duplicate service requests.

Repeat the process for the required six-month intervals until the historical period from 2022 through 2025 has been loaded.

The historical backfill is separate from the regular incremental pipeline. The backfill populates the warehouse with the historical data required for analysis, while regular Airflow runs use the `last_run_date` watermark to retrieve only new data.

### 7. Run dbt Models, Snapshots, Tests, and Documentation

Navigate to the dbt project directory:

```bash
cd dbt_project
```

Run the dbt models:

```bash
dbt run --profiles-dir .
```

Run the dbt snapshots:

```bash
dbt snapshot --profiles-dir .
```

Run the dbt tests:

```bash
dbt test --profiles-dir .
```

Generate the dbt documentation and lineage graph:

```bash
dbt docs generate --profiles-dir .
```

Serve the dbt documentation locally:

```bash
dbt docs serve --port 8085
```

Port `8085` is used to avoid conflict with the Airflow web interface running on port `8080`.

## Deliverable Questions

The project includes three analytical queries located in the `dbt_project/analyses/` directory.

### Question 1 – Resolution Time by Community Area

This analysis identifies the community areas with the slowest median resolution time for pothole and graffiti service requests and compares the results year-over-year.

Run:

```bash
dbt show --select resolution_time_by_community_area --profiles-dir .
```

### Question 2 – Duplicate Complaints by Request Type

This analysis identifies request types with a high ratio of repeated complaints at the same location within a short time window. It also compares these repeated complaints with the official duplicate indicator available in the Chicago 311 data.

Run:

```bash
dbt show --select duplicate_complaints_by_request_type --profiles-dir .
```

### Question 3 – Ward Redistricting Comparison

This analysis compares historical ward-level request volumes with the volumes obtained when request locations are reassigned using the current ward boundaries.

The comparison highlights the impact of Chicago's 2023 ward redistricting on ward-level request volumes.

Run:

```bash
dbt show --select ward_redistricting_comparison --profiles-dir . --limit 150
```

## Data Quality and Testing

The project uses dbt tests to validate the quality and consistency of the transformed Chicago 311 data.

A total of seven data tests are implemented, covering uniqueness, required fields, relationships, date consistency, geographic coordinates, and ward assignment.

The tests include:

- `not_null` validation for `sr_number`;
- `unique` validation for `sr_number`;
- a `relationships` test between service requests and the ward dimension;
- validation that `closed_date` is not earlier than `created_date`;
- validation that geographic coordinates fall within the expected Chicago area;
- validation that each request is assigned an appropriate ward version;
- `not_null` validation for `community_area`, configured with `severity: warn`.

Run all tests with:

```bash
dbt test --profiles-dir .
```

The `community_area` test is intentionally configured as a warning because some source records legitimately contain missing community area values. These records are preserved instead of causing the entire pipeline to fail.

The pipeline is also designed to be idempotent. Re-running the pipeline does not create duplicate service requests, which is validated through the uniqueness test on `sr_number`.


## How to Run from a Clean Environment

To reproduce the project from a clean environment:

1. Clone the repository.

2. Create and activate a Python 3.10 virtual environment.

3. Install the required Python dependencies.
4. Create the `.env` file and configure the required Airflow secret and Fernet keys.
5. Start the Docker environment:

```bash
docker compose up -d
```

6. Configure the Airflow Connection `socrata_chicago` and add the Socrata App Token under the `app_token` key in the Extra field.

7. Initialize the DuckDB warehouse:

```bash
python init_warehouse.py
```

8. Run the historical backfill for the required six-month intervals from 2022 through 2025:

```bash
docker compose exec airflow-scheduler python -m scripts.backfill
```

9. Navigate to the dbt project and build the transformation models:

```bash
cd dbt_project
dbt run --profiles-dir .
```

10. Run the dbt snapshots:

```bash
dbt snapshot --profiles-dir .
```

11. Validate the transformed data:

```bash
dbt test --profiles-dir .
```

12. Generate the dbt documentation:

```bash
dbt docs generate --profiles-dir .
```

13. Trigger the `chicago_311_pipeline` DAG from the Airflow interface to run the regular incremental pipeline.

14. Run the analytical queries from the `dbt_project/analyses/` directory to reproduce the three deliverable questions.