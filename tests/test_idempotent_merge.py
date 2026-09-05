import pandas as pd


def idempotent_merge(old_df, new_df):
    merged = pd.concat([old_df, new_df])

    merged = merged.drop_duplicates(
        subset=["video_id"],
        keep="last"
    )

    return merged


def test_duplicate_video_is_removed():

    old_df = pd.DataFrame({
        "video_id": ["101", "102"],
        "title": ["Old Video", "Video 2"]
    })

    new_df = pd.DataFrame({
        "video_id": ["101", "103"],
        "title": ["Updated Video", "Video 3"]
    })

    result = idempotent_merge(old_df, new_df)

    # 101 should appear only once
    assert result["video_id"].nunique() == 3

    # Latest record should be kept
    video_101 = result[result["video_id"] == "101"]

    assert video_101.iloc[0]["title"] == "Updated Video"


def test_no_duplicate_records():

    old_df = pd.DataFrame({
        "video_id": ["101", "102"],
        "title": ["Video 1", "Video 2"]
    })

    new_df = pd.DataFrame({
        "video_id": ["103", "104"],
        "title": ["Video 3", "Video 4"]
    })

    result = idempotent_merge(old_df, new_df)

    assert len(result) == 4
    assert result["video_id"].nunique() == 4