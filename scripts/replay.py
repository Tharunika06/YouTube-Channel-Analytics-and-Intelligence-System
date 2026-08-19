import os
import shutil

FAILED = "/opt/airflow/failed/failed_batch.csv"
STAGING = "/opt/airflow/staging/staged_data.csv"

if not os.path.exists(FAILED):
    print("No failed batch found.")
    exit()

shutil.copy(FAILED, STAGING)

print("Replay Successful.")
print("Failed batch copied back to staging.")