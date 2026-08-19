from kafka import KafkaProducer
from exercise4 import extract_new_data
import json

TOPIC = "youtube-data"

producer = KafkaProducer(
    bootstrap_servers="kafka:9092",
    value_serializer=lambda x: json.dumps(x).encode("utf-8")
)

print("Extracting data from YouTube...")

df = extract_new_data()

print(f"Sending {len(df)} records to Kafka...")

for _, row in df.iterrows():
    producer.send(TOPIC, row.to_dict())

producer.flush()

print("Producer Finished Successfully.")