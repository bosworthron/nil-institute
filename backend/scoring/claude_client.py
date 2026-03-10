import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

_api_key = os.getenv("ANTHROPIC_API_KEY")
client = Anthropic(api_key=_api_key) if _api_key and not _api_key.startswith("sk-ant-replace") else None

def infer_athlete_scores(athlete_data: dict) -> dict:
    """
    Uses Claude to estimate four component scores (0–100 each) for an athlete.
    Falls back to neutral scores if API key is not configured.
    """
    if client is None:
        return {
            "social_score": 50.0,
            "athletic_score": 50.0,
            "school_score": 50.0,
            "position_score": 50.0,
            "reasoning": "API key not configured — using neutral fallback scores",
        }

    prompt = f"""You are an NIL valuation analyst. Given this college athlete's data, estimate four component scores (0-100 each):

Athlete data:
{json.dumps(athlete_data, indent=2)}

Scoring criteria:
- social_score (0-100): Based on follower counts, engagement rate, platform presence. 100 = Paige Bueckers / top 0.1%
- athletic_score (0-100): Based on recruiting rank, stats, draft projection, team success. 100 = #1 overall recruit / Heisman contender
- school_score (0-100): Based on school media market size, program prestige, conference. 100 = Alabama/Ohio State in top-10 media market
- position_score (0-100): Based on NIL demand for this position/sport combo. 100 = QB or PG with elite program

Return ONLY valid JSON with no markdown:
{{"social_score": 0-100, "athletic_score": 0-100, "school_score": 0-100, "position_score": 0-100, "reasoning": "brief explanation"}}
"""
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.content[0].text.strip()
        # Strip markdown code fences if present
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {
                "social_score": 50.0,
                "athletic_score": 50.0,
                "school_score": 50.0,
                "position_score": 50.0,
                "reasoning": "Failed to parse Claude response — using neutral fallback",
            }
    except Exception as api_err:
        print(f"    [claude_client] API error ({api_err.__class__.__name__}): {api_err} — using neutral fallback scores")
        return {
            "social_score": 50.0,
            "athletic_score": 50.0,
            "school_score": 50.0,
            "position_score": 50.0,
            "reasoning": f"API error — using neutral fallback scores",
        }
