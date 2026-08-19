import requests
import pandas as pd
import time

# -----------------------------
# Configuration
# -----------------------------

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"
CATEGORIES_URL = "https://www.googleapis.com/youtube/v3/videoCategories"

SEARCH_KEYWORD = "Data Engineering"
MAX_RESULTS = 20

    
API_KEY = "AIzaSyDtzLoirwOY3k4DQYXKVv6ts0dWa2umNsI"

# -----------------------------
# Get Video IDs
# -----------------------------

def get_video_ids(keyword, api_key, max_results):

    video_ids = []
    next_page_token = None

    while len(video_ids) < max_results:

        params = {
            "part": "id",
            "q": keyword,
            "type": "video",
            "maxResults": 50,
            "key": api_key
        }

        if next_page_token:
            params["pageToken"] = next_page_token

        response = requests.get(
            SEARCH_URL,
            params=params,
            timeout=15
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Search API Error ({response.status_code})\n{response.text}"
            )

        data = response.json()

        ids = [
            item["id"]["videoId"]
            for item in data.get("items", [])
            if item.get("id", {}).get("videoId")
        ]

        video_ids.extend(ids)

        next_page_token = data.get("nextPageToken")

        if not next_page_token:
            break

        time.sleep(0.2)

    return video_ids[:max_results]


# -----------------------------
# Category Mapping
# -----------------------------

def get_category_map(api_key, region_code="US"):

    params = {
        "part": "snippet",
        "regionCode": region_code,
        "key": api_key
    }

    response = requests.get(
        CATEGORIES_URL,
        params=params,
        timeout=15
    )

    category_map = {}

    if response.status_code == 200:

        for item in response.json().get("items", []):

            category_map[item["id"]] = item["snippet"]["title"]

    return category_map


# -----------------------------
# Get Video Details
# -----------------------------

def get_video_details(video_ids, api_key):

    all_items = []

    for i in range(0, len(video_ids), 50):

        batch_ids = video_ids[i:i + 50]

        params = {
            "part": "snippet,contentDetails,statistics,status",
            "id": ",".join(batch_ids),
            "key": api_key
        }

        response = requests.get(
            VIDEOS_URL,
            params=params,
            timeout=15
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Videos API Error ({response.status_code})\n{response.text}"
            )

        all_items.extend(response.json().get("items", []))

        time.sleep(0.2)

    return all_items


# -----------------------------
# Parse Video
# -----------------------------

def parse_video_item(item, category_map):

    snippet = item.get("snippet", {})
    content = item.get("contentDetails", {})
    stats = item.get("statistics", {})
    status = item.get("status", {})

    video_id = item.get("id", "")

    return {

        "video_id": video_id,

        "video_url":
        f"https://www.youtube.com/watch?v={video_id}",

        "title":
        snippet.get("title"),

        "description":
        snippet.get("description"),

        "channel_id":
        snippet.get("channelId"),

        "channel_name":
        snippet.get("channelTitle"),

        "published_at":
        snippet.get("publishedAt"),

        "category_id":
        snippet.get("categoryId"),

        "category_name":
        category_map.get(
            snippet.get("categoryId"),
            "Unknown"
        ),

        "thumbnail_url":
        snippet.get("thumbnails", {})
        .get("high", {})
        .get("url"),

        "tags":
        ",".join(snippet.get("tags", []))
        if snippet.get("tags")
        else None,

        "duration":
        content.get("duration"),

        "view_count":
        stats.get("viewCount"),

        "like_count":
        stats.get("likeCount"),

        "comment_count":
        stats.get("commentCount"),

        "favorite_count":
        stats.get("favoriteCount"),

        "default_language":
        snippet.get("defaultLanguage"),

        "default_audio_language":
        snippet.get("defaultAudioLanguage"),

        "caption_available":
        content.get("caption"),

        "licensed_content":
        content.get("licensedContent"),

        "privacy_status":
        status.get("privacyStatus"),

        "definition":
        content.get("definition"),

        "dimension":
        content.get("dimension")

    }


# -----------------------------
# Main Extraction Function
# -----------------------------

def extract_new_data(
    keyword=SEARCH_KEYWORD,
    api_key=API_KEY,
    max_results=MAX_RESULTS
):

    video_ids = get_video_ids(
        keyword,
        api_key,
        max_results
    )

    if not video_ids:
        raise RuntimeError("No videos found.")

    category_map = get_category_map(api_key)

    raw_items = get_video_details(
        video_ids,
        api_key
    )

    if not raw_items:
        raise RuntimeError("No video details returned.")

    records = [
        parse_video_item(item, category_map)
        for item in raw_items
    ]

    df = pd.DataFrame(records)

    print(f"Extracted {len(df)} videos successfully.")

    return df


# -----------------------------
# Test
# -----------------------------

if __name__ == "__main__":

    df = extract_new_data()

    print(df.head())

    print(df.columns)

    print(df.shape)
    
