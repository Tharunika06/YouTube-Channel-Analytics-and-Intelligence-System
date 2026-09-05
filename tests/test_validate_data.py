
import pandas as pd
import pytest

from scripts.validate_data import validate_data, EXPECTED_COLUMNS


def create_valid_data():
    return pd.DataFrame({
        "video_id": ["101", "102", "103"],
        "video_url": ["url1", "url2", "url3"],
        "title": ["Video 1", "Video 2", "Video 3"],
        "description": ["Desc 1", "Desc 2", "Desc 3"],
        "channel_id": ["ch1", "ch1", "ch1"],
        "channel_name": ["Channel", "Channel", "Channel"],
        "published_at": ["2026-01-01"] * 3,
        "category_id": [1, 1, 1],
        "category_name": ["Music"] * 3,
        "thumbnail_url": ["img1", "img2", "img3"],
        "tags": ["tag1", "tag2", "tag3"],
        "duration": ["PT1M", "PT2M", "PT3M"],
        "view_count": [100, 200, 300],
        "like_count": [10, 20, 30],
        "comment_count": [5, 10, 15],
        "favorite_count": [0, 0, 0],
        "default_language": ["en"] * 3,
        "default_audio_language": ["en"] * 3,
        "caption_available": [True] * 3,
        "licensed_content": [True] * 3,
        "privacy_status": ["public"] * 3,
        "definition": ["hd"] * 3,
        "dimension": ["2d"] * 3
    })


def test_valid_data():
    df = create_valid_data()

    result = validate_data(df)

    assert len(result) == 3
    assert list(result.columns) == EXPECTED_COLUMNS


def test_missing_column():
    df = create_valid_data()

    df = df.drop(columns=["video_id"])

    with pytest.raises(ValueError, match="Schema Validation Failed"):
        validate_data(df)


def test_null_validation():
    df = create_valid_data()

    df.loc[0, "video_id"] = None

    result = validate_data(df)

    assert len(result) == 2
    assert result["video_id"].isnull().sum() == 0


def test_all_rows_null():
    df = create_valid_data()

    df["video_id"] = None
    df["title"] = None
    df["channel_name"] = None
    df["view_count"] = None

    with pytest.raises(ValueError, match="All rows failed Null Validation"):
        validate_data(df)

