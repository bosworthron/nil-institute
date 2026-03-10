import pytest
from backend.scoring.engine import calculate_nil_score, composite_to_dollars, compute_score_delta

def test_composite_score_all_max():
    score = calculate_nil_score(
        social_score=100.0,
        athletic_score=100.0,
        school_score=100.0,
        position_score=100.0,
    )
    assert score == 100.0

def test_composite_score_social_only():
    score = calculate_nil_score(
        social_score=100.0,
        athletic_score=0.0,
        school_score=0.0,
        position_score=0.0,
    )
    assert score == 35.0  # 35% weight for social

def test_composite_score_weights_sum_to_one():
    """Verify weights sum to exactly 1.0 by checking max input = max output."""
    score = calculate_nil_score(100.0, 100.0, 100.0, 100.0)
    assert score == 100.0

def test_composite_to_dollars_max():
    dollars = composite_to_dollars(100.0)
    assert dollars == 5_000_000.0

def test_composite_to_dollars_zero():
    dollars = composite_to_dollars(0.0)
    assert dollars == 0.0

def test_composite_to_dollars_midrange():
    dollars = composite_to_dollars(50.0)
    # 5_000_000 * (0.5 ** 2.2) — should be less than 1.25M (non-linear)
    assert dollars < 1_250_000

def test_score_delta_positive():
    delta = compute_score_delta(old_score=800000, new_score=847000)
    assert round(delta, 2) == 5.88

def test_score_delta_negative():
    delta = compute_score_delta(old_score=847000, new_score=800000)
    assert round(delta, 2) == -5.55

def test_score_delta_no_previous():
    delta = compute_score_delta(old_score=None, new_score=847000)
    assert delta == 0.0

def test_score_delta_zero_old():
    delta = compute_score_delta(old_score=0, new_score=500000)
    assert delta == 0.0

def test_composite_score_clamps_over_100():
    """Scores above 100 should be clamped, not produce inflated results."""
    score = calculate_nil_score(200.0, 200.0, 200.0, 200.0)
    assert score == 100.0

def test_composite_to_dollars_nan_safe():
    import math
    result = composite_to_dollars(float("nan"))
    assert result == 0.0

def test_weights_sum_to_one():
    from backend.scoring.engine import WEIGHTS
    assert sum(WEIGHTS.values()) == 1.0
