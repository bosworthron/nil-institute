import pytest
from backend.scrapers.pipeline import normalize_athlete_data

def test_normalize_complete_data():
    raw = {
        "name": "John Smith",
        "school": "Alabama",
        "sport": "football",
        "position": "QB",
        "year": "Junior",
        "conference": "SEC",
        "instagram_followers": 50000,
        "twitter_followers": 20000,
        "engagement_rate": 3.5,
    }
    result = normalize_athlete_data(raw)
    assert result["name"] == "John Smith"
    assert result["id"] == "john-smith-alabama-football"
    assert result["instagram_followers"] == 50000
    assert result["sport"] == "football"

def test_normalize_missing_social_defaults_to_zero():
    raw = {
        "name": "Jane Doe",
        "school": "Stanford",
        "sport": "basketball",
        "position": "PG",
    }
    result = normalize_athlete_data(raw)
    assert result["instagram_followers"] == 0
    assert result["twitter_followers"] == 0
    assert result["engagement_rate"] == 0.0

def test_normalize_id_generation_special_chars():
    raw = {
        "name": "O'Brien Jr.",
        "school": "Notre Dame",
        "sport": "football",
        "position": "TE",
    }
    result = normalize_athlete_data(raw)
    # ID should only contain lowercase alphanumeric and hyphens
    import re
    assert re.match(r'^[a-z0-9\-]+$', result["id"])
    assert "notre-dame" in result["id"]

def test_normalize_preserves_optional_fields():
    raw = {
        "name": "Test Player",
        "school": "Ohio State",
        "sport": "football",
        "position": "WR",
        "recruiting_rank": 5,
        "instagram_handle": "testplayer",
    }
    result = normalize_athlete_data(raw)
    assert result["recruiting_rank"] == 5
    assert result["instagram_handle"] == "testplayer"

def test_normalize_missing_optional_fields_are_none():
    raw = {
        "name": "Test Player",
        "school": "Ohio State",
        "sport": "football",
    }
    result = normalize_athlete_data(raw)
    assert result["recruiting_rank"] is None
    assert result["instagram_handle"] is None
    assert result["conference"] is None

def test_normalize_raises_on_empty_id():
    import pytest
    with pytest.raises(ValueError):
        normalize_athlete_data({"name": "---", "school": "---", "sport": "---"})

def test_normalize_tiktok_followers_default():
    raw = {"name": "Test", "school": "UCLA", "sport": "football"}
    result = normalize_athlete_data(raw)
    assert result["tiktok_followers"] == 0
