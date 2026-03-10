import re
from typing import Optional

def normalize_athlete_data(raw: dict) -> dict:
    """
    Normalize raw scraped data into a consistent athlete record.
    Generates a stable ID from name + school + sport.
    """
    name = raw.get("name", "").strip()
    school = raw.get("school", "").strip()
    sport = raw.get("sport", "").strip()

    # Generate stable ID: lowercase alphanumeric + hyphens only
    id_source = f"{name} {school} {sport}".lower()
    athlete_id = re.sub(r"[^a-z0-9]+", "-", id_source).strip("-")

    return {
        "id": athlete_id,
        "name": name,
        "school": school,
        "conference": raw.get("conference"),
        "sport": sport,
        "position": raw.get("position"),
        "year": raw.get("year"),
        "instagram_handle": raw.get("instagram_handle"),
        "twitter_handle": raw.get("twitter_handle"),
        "tiktok_handle": raw.get("tiktok_handle"),
        "instagram_followers": raw.get("instagram_followers", 0),
        "twitter_followers": raw.get("twitter_followers", 0),
        "engagement_rate": raw.get("engagement_rate", 0.0),
        "recruiting_rank": raw.get("recruiting_rank"),
    }
