import pandas as pd
import os
import shutil

# -----------------------------
# File Paths
# -----------------------------

VALIDATED = "/opt/airflow/validated/validated_batch_latest.csv"

WAREHOUSE_DIR = "/opt/airflow/warehouse"

WAREHOUSE = os.path.join(
    WAREHOUSE_DIR,
    "youtube_warehouse.csv"
)

TEMP = os.path.join(
    WAREHOUSE_DIR,
    "temp.csv"
)

os.makedirs(WAREHOUSE_DIR, exist_ok=True)

# -----------------------------
# Read validated data
# -----------------------------

new_df = pd.read_csv(VALIDATED)
if new_df.empty:
    print("Nothing to merge.")
    exit(0)
print(f"Incoming Records : {len(new_df)}")

# -----------------------------
# First Load
# -----------------------------

if not os.path.exists(WAREHOUSE):

    shutil.copy(VALIDATED, WAREHOUSE)

    print("First Load Completed")

else:

    old_df = pd.read_csv(WAREHOUSE)

    print(f"Existing Records : {len(old_df)}")

    merged = pd.concat([old_df, new_df])

    # -----------------------------
    # Idempotent Merge
    # -----------------------------

    merged = merged.drop_duplicates(
        subset=["video_id"],
        keep="last"
    )

    print(f"After Merge : {len(merged)}")

    # -----------------------------
    # Atomic Transaction
    # -----------------------------

    merged.to_csv(TEMP, index=False)

    os.replace(TEMP, WAREHOUSE)

    print("Warehouse Updated Atomically")

print("Pipeline Load Successful")