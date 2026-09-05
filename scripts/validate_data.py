import pandas as pd
import os
import shutil

STAGING_FILE = "/opt/airflow/staging/staged_data.csv"

FAILED_DIR = "/opt/airflow/failed"
FAILED_FILE = "/opt/airflow/failed/failed_batch.csv"

VALIDATED_DIR = "/opt/airflow/validated"
VALIDATED_FILE = "/opt/airflow/validated/validated_batch_latest.csv"


EXPECTED_COLUMNS = [
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

CRITICAL_COLUMNS = [
    "video_id",
    "title",
    "channel_name",
    "view_count"
]


def validate_data(df):

    # Schema validation
    missing = [
        col for col in EXPECTED_COLUMNS
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Schema Validation Failed. Missing Columns: {missing}"
        )

    # Null validation
    df = df.dropna(subset=CRITICAL_COLUMNS)

    if len(df) == 0:
        raise ValueError(
            "All rows failed Null Validation."
        )

    # Outlier detection
    df = df.copy()

    df["view_count"] = pd.to_numeric(
        df["view_count"],
        errors="coerce"
    )

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
        raise ValueError(
            "All rows removed as Outliers."
        )

    return validated_df


def run_validation():

    try:

        df = pd.read_csv(STAGING_FILE)

        print(f"Loaded {len(df)} rows from staging.")

        validated_df = validate_data(df)

        os.makedirs(VALIDATED_DIR, exist_ok=True)

        validated_df.to_csv(
            VALIDATED_FILE,
            index=False
        )

        print(
            f"Saved validated data to {VALIDATED_FILE}"
        )

        print("Validation Completed Successfully")

    except Exception as e:

        os.makedirs(FAILED_DIR, exist_ok=True)

        if os.path.exists(STAGING_FILE):
            shutil.copy(
                STAGING_FILE,
                FAILED_FILE
            )

        print("Validation Failed")
        print(e)
        print(
            f"Failed batch stored in {FAILED_FILE}"
        )


if __name__ == "__main__":
    run_validation()

