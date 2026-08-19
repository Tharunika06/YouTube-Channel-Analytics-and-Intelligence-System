import pandas as pd
import os
import shutil

# -------------------------------------
# File Paths
# -------------------------------------

STAGING_FILE = "/opt/airflow/staging/staged_data.csv"

FAILED_DIR = "/opt/airflow/failed"
FAILED_FILE = "/opt/airflow/failed/failed_batch.csv"

VALIDATED_DIR = "/opt/airflow/validated"
VALIDATED_FILE = "/opt/airflow/validated/validated_batch_latest.csv"

try:

    # -------------------------------------
    # Read staged file
    # -------------------------------------

    df = pd.read_csv(STAGING_FILE)
    print(f"Loaded {len(df)} rows from staging.")

    # -------------------------------------
    # Schema Validation
    # -------------------------------------

    expected_columns = [
        "video_id",
        "video_url",
        "title",
        "description",
        "channel_id",
        "channel_name",
        "published_at",
        "category_id",
        "category_name",
        "thumbnail_url",
        "tags",
        "duration",
        "view_count",
        "like_count",
        "comment_count",
        "favorite_count",
        "default_language",
        "default_audio_language",
        "caption_available",
        "licensed_content",
        "privacy_status",
        "definition",
        "dimension"
    ]

    missing = []

    for col in expected_columns:
        if col not in df.columns:
            missing.append(col)

    if len(missing) > 0:
        raise Exception(f"Schema Validation Failed.\nMissing Columns: {missing}")

    print("Schema Validation Passed")

    # -------------------------------------
    # Null Validation
    # -------------------------------------

    critical_columns = [
        "video_id",
        "title",
        "channel_name",
        "view_count"
    ]

    df = df.dropna(subset=critical_columns)

    if len(df) == 0:
        raise Exception("All rows failed Null Validation.")

    print(f"Rows after Null Check : {len(df)}")

    # -------------------------------------
    # Outlier Detection
    # -------------------------------------

    df["view_count"] = pd.to_numeric(df["view_count"], errors="coerce")

    Q1 = df["view_count"].quantile(0.25)
    Q3 = df["view_count"].quantile(0.75)

    IQR = Q3 - Q1

    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

    validated_df = df[
        (df["view_count"] >= lower) &
        (df["view_count"] <= upper)
    ]

    if len(validated_df) == 0:
        raise Exception("All rows removed as Outliers.")

    print(f"Rows after Outlier Removal : {len(validated_df)}")

    # -------------------------------------
    # Save Validated Batch
    # -------------------------------------

    os.makedirs(VALIDATED_DIR, exist_ok=True)

    validated_df.to_csv(
        VALIDATED_FILE,
        index=False
    )

    print(f"Saved validated data to {VALIDATED_FILE}")
    print("Validation Completed Successfully")

# -------------------------------------
# Error Handling
# -------------------------------------

except Exception as e:

    os.makedirs(FAILED_DIR, exist_ok=True)

    if os.path.exists(STAGING_FILE):
        shutil.copy(STAGING_FILE, FAILED_FILE)

    print("Validation Failed")
    print(e)
    print(f"Failed batch stored in {FAILED_FILE}")