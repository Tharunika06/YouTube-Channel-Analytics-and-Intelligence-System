import pandas as pd
import sqlite3
import os

# -----------------------------
# Paths
# -----------------------------

WAREHOUSE_FILE = "/opt/airflow/warehouse/youtube_warehouse.csv"

DB_DIR = "/opt/airflow/database"
DB_NAME = os.path.join(DB_DIR, "youtube_pipeline.db")

TABLE_NAME = "youtube_videos"

# -----------------------------
# Create database folder
# -----------------------------

os.makedirs(DB_DIR, exist_ok=True)

# -----------------------------
# Check warehouse file
# -----------------------------

if not os.path.exists(WAREHOUSE_FILE):
    raise FileNotFoundError(
        f"Warehouse file not found:\n{WAREHOUSE_FILE}"
    )

# -----------------------------
# Read Warehouse
# -----------------------------

df = pd.read_csv(WAREHOUSE_FILE)
if df.empty:
    print("Warehouse empty.")
    exit(0)
print(f"Loaded {len(df)} records from warehouse.")

# -----------------------------
# Connect SQLite
# -----------------------------

conn = sqlite3.connect(DB_NAME)

try:

    # Replace existing table
    df.to_sql(
        TABLE_NAME,
        conn,
        if_exists="replace",
        index=False
    )

    conn.commit()

    print("SQLite Load Successful")

    # Verification
    count = pd.read_sql(
        f"SELECT COUNT(*) AS total FROM {TABLE_NAME}",
        conn
    )

    print(f"Rows in SQLite : {count.iloc[0]['total']}")

except Exception as e:

    conn.rollback()
    print("SQLite Load Failed")
    print(e)

finally:
    conn.close()

print(f"Database Location : {DB_NAME}")