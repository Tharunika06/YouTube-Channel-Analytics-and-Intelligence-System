from kafka import KafkaConsumer
import pandas as pd
import json
import os
import uuid

# -----------------------------
# Configuration
# -----------------------------

TOPIC = "youtube-data"

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers="kafka:29092",
    auto_offset_reset="earliest",
    enable_auto_commit=False,
    group_id=f"pipeline-{uuid.uuid4()}",
    consumer_timeout_ms=10000,
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

# -----------------------------
# Read Kafka Messages
# -----------------------------

records = []

print("=" * 50)
print("Waiting for Kafka messages...")
print("=" * 50)

for message in consumer:
    print("Received:", message.value)
    records.append(message.value)

consumer.close()

print("=" * 50)
print(f"Messages received : {len(records)}")
print("=" * 50)

# -----------------------------
# Create staging folder
# -----------------------------

STAGING_DIR = "/opt/airflow/staging"
os.makedirs(STAGING_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(STAGING_DIR, "staged_data.csv")

# -----------------------------
# No messages
# -----------------------------

if len(records) == 0:
    print("No new Kafka messages.")
    exit(0)

# -----------------------------
# Save to staging
# -----------------------------

df = pd.DataFrame(records)

df.to_csv(OUTPUT_FILE, index=False)

print(df)

print("=" * 50)
print(f"Saved {len(df)} records to")
print(OUTPUT_FILE)
print("=" * 50)