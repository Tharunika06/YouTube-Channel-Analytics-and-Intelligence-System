import streamlit as st
from kafka import KafkaProducer
import json
import requests
import uuid
from requests.auth import HTTPBasicAuth

# ---------------------------------
# Kafka Producer
# ---------------------------------

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

TOPIC = "youtube-data"

# ---------------------------------
# Streamlit UI
# ---------------------------------

st.set_page_config(
    page_title="YouTube Analytics Portal",
    page_icon="📺",
    layout="wide"
)

st.title("YouTube Channel Analytics Portal")
st.write("Enter new YouTube video details.")

with st.form("video_form"):

    video_id = st.text_input("Video ID")
    title = st.text_input("Video Title")
    channel_name = st.text_input("Channel Name")
    category = st.text_input("Category")

    view_count = st.number_input("Views", min_value=0)
    like_count = st.number_input("Likes", min_value=0)
    comment_count = st.number_input("Comments", min_value=0)

    submit = st.form_submit_button("Submit")

# ---------------------------------
# Submit
# ---------------------------------

if submit:

    data = {
        "video_id": video_id,
        "video_url": "",
        "title": title,
        "description": "",
        "channel_id": "",
        "channel_name": channel_name,
        "published_at": "",
        "category_id": "",
        "category_name": category,
        "thumbnail_url": "",
        "tags": "",
        "duration": "",
        "view_count": int(view_count),
        "like_count": int(like_count),
        "comment_count": int(comment_count),
        "favorite_count": 0,
        "default_language": "en",
        "default_audio_language": "en",
        "caption_available": True,
        "licensed_content": True,
        "privacy_status": "public",
        "definition": "hd",
        "dimension": "2d"
    }

    # -----------------------------
    # Send to Kafka
    # -----------------------------

    producer.send(TOPIC, data)
    producer.flush()

    st.success("✅ Data sent to Kafka successfully!")

    # -----------------------------
    # Trigger Airflow
    # -----------------------------

    airflow_url = "http://localhost:8080/api/v1/dags/production_pipeline/dagRuns"

    payload = {
        "dag_run_id": f"manual_{uuid.uuid4()}",
        "conf": {}
    }

    try:

        response = requests.post(
            airflow_url,
            auth=HTTPBasicAuth("admin", "admin"),
            json=payload,
            timeout=10
        )

        st.write("Status Code:", response.status_code)
        st.write("Response:")
        st.code(response.text)

        if response.status_code in [200, 201]:
            st.success("✅ Airflow DAG Triggered Successfully!")
        else:
            st.error("❌ Failed to trigger Airflow")

    except requests.exceptions.RequestException as e:
        st.error("❌ Unable to connect to Airflow")
        st.exception(e)