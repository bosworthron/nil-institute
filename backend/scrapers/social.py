"""
Social media data module.

Phase 1 (current): Provides estimated social presence based on athlete profile.
Phase 2: Integrate social media API or scraping service.
"""

def estimate_social_presence(
    athlete_name: str,
    school: str,
    sport: str,
    position: str,
) -> dict:
    """
    Phase 1 stub — social data will be filled in by Claude AI inference
    in the scoring pipeline via infer_athlete_scores().
    """
    return {
        "instagram_followers": 0,
        "twitter_followers": 0,
        "tiktok_followers": 0,
        "engagement_rate": 0.0,
        "social_estimated": True,
    }
