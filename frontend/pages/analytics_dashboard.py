import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

# ----------------------------------------
# Page Configuration
# ----------------------------------------

st.set_page_config(
    page_title="YouTube Analytics Dashboard",
    page_icon="▶️",
    layout="wide"
)

# ----------------------------------------
# Database
# ----------------------------------------

DB_PATH = r"D:\DE\ProductionPipeline\database\youtube_pipeline.db"

# ----------------------------------------
# Load Data
# ----------------------------------------

@st.cache_data(ttl=5)
def load_data():
    conn = sqlite3.connect(DB_PATH)

    query = """
        SELECT *
        FROM youtube_videos
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df


df = load_data()

# ----------------------------------------
# Page Title
# ----------------------------------------

st.markdown(
    """
    <h1 style="
        color:white;
        font-size:32px;
        margin-bottom:0;
    ">
    ▶ YouTube Channel Analytics and Intelligence System
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <p style="color:#AAAAAA;">
    Streamlit → Kafka → Airflow → SQLite → Analytics
    </p>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# ----------------------------------------
# Refresh
# ----------------------------------------

if st.button("🔄 Refresh Dashboard"):
    st.cache_data.clear()
    st.rerun()

# ----------------------------------------
# KPI Calculations
# ----------------------------------------

total_videos = len(df)

total_views = df["view_count"].sum()

total_likes = df["like_count"].sum()

total_comments = df["comment_count"].sum()

engagement_rate = (
    (total_likes + total_comments) / total_views * 100
    if total_views > 0
    else 0
)

# ----------------------------------------
# KPI Cards
# ----------------------------------------

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Videos", f"{total_videos:,}")

with col2:
    st.metric("Total Views", f"{total_views/1_000_000:.2f}M")

with col3:
    st.metric("Total Likes", f"{total_likes/1_000:.2f}K")

with col4:
    st.metric("Total Comments", f"{total_comments/1_000:.2f}K")

with col5:
    st.metric("Engagement Rate", f"{engagement_rate:.2f}%")

st.markdown("---")

# ----------------------------------------
# Filters
# ----------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    channels = ["All"] + sorted(
        df["channel_name"].dropna().astype(str).unique().tolist()
    )

    selected_channel = st.selectbox(
        "Channel",
        channels
    )

with col2:
    categories = ["All"] + sorted(
        df["category_name"].dropna().astype(str).unique().tolist()
    )

    selected_category = st.selectbox(
        "Category",
        categories
    )

with col3:
    years = ["All"]

    if "published_at" in df.columns:
        years += sorted(
            pd.to_datetime(
                df["published_at"],
                errors="coerce"
            )
            .dt.year
            .dropna()
            .astype(int)
            .astype(str)
            .unique()
            .tolist()
        )

    selected_year = st.selectbox(
        "Published Year",
        years
    )

# ----------------------------------------
# Apply Filters
# ----------------------------------------

filtered_df = df.copy()

if selected_channel != "All":
    filtered_df = filtered_df[
        filtered_df["channel_name"] == selected_channel
    ]

if selected_category != "All":
    filtered_df = filtered_df[
        filtered_df["category_name"] == selected_category
    ]

if selected_year != "All":
    years_data = pd.to_datetime(
        filtered_df["published_at"],
        errors="coerce"
    ).dt.year

    filtered_df = filtered_df[
        years_data == int(selected_year)
    ]

# ----------------------------------------
# Charts
# ----------------------------------------

col1, col2 = st.columns(2)

with col1:

    top_videos = (
        filtered_df
        .groupby("title", dropna=True)["view_count"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig = px.bar(
        top_videos,
        x="view_count",
        y="title",
        orientation="h",
        title="Top 10 Videos by Views"
    )

    fig.update_layout(
        template="plotly_dark",
        height=400,
        yaxis={"categoryorder": "total ascending"}
    )

    st.plotly_chart(fig, use_container_width=True)


with col2:

    top_channels = (
        filtered_df
        .groupby("channel_name", dropna=True)["view_count"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig = px.bar(
        top_channels,
        x="view_count",
        y="channel_name",
        orientation="h",
        title="Top Channels by Total Views"
    )

    fig.update_layout(
        template="plotly_dark",
        height=400,
        yaxis={"categoryorder": "total ascending"}
    )

    st.plotly_chart(fig, use_container_width=True)


col1, col2 = st.columns(2)

with col1:

    category_data = (
        filtered_df
        .groupby("category_name")
        .size()
        .reset_index(name="video_count")
    )

    fig = px.pie(
        category_data,
        names="category_name",
        values="video_count",
        hole=0.5,
        title="Videos by Category"
    )

    fig.update_layout(
        template="plotly_dark",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)


with col2:

    fig = px.scatter(
        filtered_df,
        x="view_count",
        y="like_count",
        hover_name="title",
        title="Views vs Likes"
    )

    fig.update_layout(
        template="plotly_dark",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)


col1, col2 = st.columns(2)

with col1:

    if "published_at" in filtered_df.columns:

        trend = filtered_df.copy()

        trend["published_at"] = pd.to_datetime(
            trend["published_at"],
            errors="coerce"
        )

        trend = (
            trend.dropna(subset=["published_at"])
            .groupby(trend["published_at"].dt.to_period("M"))
            .size()
            .reset_index(name="video_count")
        )

        trend["published_at"] = trend["published_at"].astype(str)

        fig = px.line(
            trend,
            x="published_at",
            y="video_count",
            markers=True,
            title="Videos Published Over Time"
        )

        fig.update_layout(
            template="plotly_dark",
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)


with col2:

    channel_data = (
        filtered_df
        .groupby("channel_name")["view_count"]
        .sum()
        .reset_index()
    )

    fig = px.treemap(
        channel_data,
        path=["channel_name"],
        values="view_count",
        title="Channel-wise Contribution"
    )

    fig.update_layout(
        template="plotly_dark",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------
# Latest Records
# ----------------------------------------

st.markdown("---")

st.subheader("Latest Pipeline Records")

st.dataframe(
    filtered_df[
        [
            "video_id",
            "title",
            "channel_name",
            "category_name",
            "view_count",
            "like_count",
            "comment_count"
        ]
    ].tail(10),
    use_container_width=True
)