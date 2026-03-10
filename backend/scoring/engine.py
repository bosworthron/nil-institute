from typing import Optional

WEIGHTS = {
    "social": 0.35,
    "athletic": 0.30,
    "school": 0.20,
    "position": 0.15,
}

# NIL score ceiling — top athletes (Paige Bueckers tier) approach this
MAX_NIL_VALUE = 5_000_000.0

def calculate_nil_score(
    social_score: float,
    athletic_score: float,
    school_score: float,
    position_score: float,
) -> float:
    """
    Returns a normalized composite score (0–100).
    Weights: social 35%, athletic 30%, school 20%, position 15%.
    """
    # Clamp all inputs to valid 0–100 range
    social_score = max(0.0, min(100.0, social_score))
    athletic_score = max(0.0, min(100.0, athletic_score))
    school_score = max(0.0, min(100.0, school_score))
    position_score = max(0.0, min(100.0, position_score))

    composite = (
        social_score * WEIGHTS["social"]
        + athletic_score * WEIGHTS["athletic"]
        + school_score * WEIGHTS["school"]
        + position_score * WEIGHTS["position"]
    )
    return round(composite, 4)

def composite_to_dollars(composite_score: float) -> float:
    """
    Convert 0–100 composite score to estimated NIL dollar value.
    Uses exponential scaling so top athletes earn disproportionately more.
    """
    if not composite_score or composite_score <= 0 or composite_score != composite_score:  # NaN check
        return 0.0
    composite_score = min(100.0, composite_score)
    normalized = composite_score / 100.0
    dollar_value = MAX_NIL_VALUE * (normalized ** 2.2)
    return round(dollar_value, 0)

def compute_score_delta(old_score: Optional[float], new_score: float) -> float:
    """Returns % change between old and new score. Returns 0.0 if no prior score."""
    if old_score is None or old_score == 0:
        return 0.0
    delta = ((new_score - old_score) / old_score) * 100
    return round(delta, 2)
