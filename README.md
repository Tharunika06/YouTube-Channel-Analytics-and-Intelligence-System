# YouTube Channel Analytics and Intelligence System

An automated end-to-end YouTube data engineering pipeline that collects video data through Streamlit, streams it using Apache Kafka, processes and validates it using Apache Airflow, stores the processed data in SQLite, and presents the results through an interactive Streamlit analytics dashboard.

---

## Project Overview

The **YouTube Channel Analytics and Intelligence System** is designed to automate the complete journey of YouTube video data from user input to analytics.

The system allows users to enter YouTube video details through a Streamlit application. The submitted data is sent to Kafka, processed through an Airflow-managed ETL pipeline, validated and deduplicated, and finally stored in a SQLite database. The processed database is then used by the analytics dashboard to display updated KPIs and visual insights.

The main objective is to reduce manual processing and demonstrate a reliable, automated data engineering workflow.

---

## Objectives

- Build an automated end-to-end YouTube data pipeline.
- Collect video data through a user-friendly Streamlit interface.
- Use Apache Kafka for data streaming and messaging.
- Use Apache Airflow for pipeline orchestration.
- Perform data validation and quality checks.
- Implement idempotent processing to prevent duplicate records.
- Store processed data in a structured SQLite database.
- Develop an interactive dashboard for YouTube analytics.
- Demonstrate dynamic updates from user input to database and dashboard.

---

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Data processing and pipeline scripts |
| Pandas | Data cleaning and transformation |
| Streamlit | Data input and analytics dashboard |
| Apache Kafka | Data streaming and messaging |
| Apache Airflow | Workflow orchestration |
| SQLite | Final database storage |
| Docker | Containerization and service management |
| Plotly | Interactive dashboard visualizations |
| PostgreSQL | Airflow metadata database |

---

## System Architecture

The complete data flow is:

```text
Streamlit Input
       ↓
Kafka Producer
       ↓
Kafka Topic (youtube-data)
       ↓
YouTube Consumer
       ↓
Staging
       ↓
Data Validation
       ↓
Idempotent Merge / Deduplication
       ↓
Warehouse
       ↓
Load SQLite
       ↓
SQLite Database
       ↓
Streamlit Analytics Dashboard