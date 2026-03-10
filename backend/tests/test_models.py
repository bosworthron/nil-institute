import pytest
from backend.db.models import Athlete, ScoreHistory

def test_athlete_model_fields():
    athlete = Athlete(
        id="test-123",
        name="John Smith",
        school="Alabama",
        sport="football",
        position="QB",
        year="Junior",
        instagram_handle="johnsmith",
        twitter_handle="johnsmith",
        current_score=847000.0,
        score_change_pct=5.2,
    )
    assert athlete.name == "John Smith"
    assert athlete.current_score == 847000.0

def test_score_history_model_fields():
    history = ScoreHistory(
        athlete_id="test-123",
        score=847000.0,
        week_date="2026-03-10",
    )
    assert history.athlete_id == "test-123"
