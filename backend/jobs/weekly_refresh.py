"""
Weekly NIL score refresh job.
Run with: PYTHONPATH=. backend/venv/Scripts/python -m backend.jobs.weekly_refresh
Scheduled: every Monday at 3am EST via Railway cron.
"""
import asyncio
import os
import sys
from datetime import date

from dotenv import load_dotenv
load_dotenv("backend/.env")

from backend.db.models import Athlete, ScoreHistory
from backend.scoring.engine import calculate_nil_score, composite_to_dollars, compute_score_delta
from backend.scoring.claude_client import infer_athlete_scores
from backend.scrapers.pipeline import normalize_athlete_data

# Seed athletes for Phase 1 — expands as scrapers mature
SEED_ATHLETES = [
    {
        "name": "Travis Hunter",
        "school": "Colorado",
        "sport": "football",
        "position": "WR/CB",
        "year": "Junior",
        "conference": "Big 12",
        "instagram_followers": 1200000,
        "twitter_followers": 450000,
        "engagement_rate": 4.2,
        "recruiting_rank": 1,
    },
    {
        "name": "Arch Manning",
        "school": "Texas",
        "sport": "football",
        "position": "QB",
        "year": "Sophomore",
        "conference": "SEC",
        "instagram_followers": 890000,
        "twitter_followers": 320000,
        "engagement_rate": 3.8,
        "recruiting_rank": 1,
    },
    {
        "name": "Cooper Flagg",
        "school": "Duke",
        "sport": "basketball",
        "position": "SF",
        "year": "Freshman",
        "conference": "ACC",
        "instagram_followers": 750000,
        "twitter_followers": 280000,
        "engagement_rate": 5.1,
        "recruiting_rank": 1,
    },
    {
        "name": "Drayden Pierce",
        "school": "Alabama",
        "sport": "football",
        "position": "QB",
        "year": "Junior",
        "conference": "SEC",
        "instagram_followers": 95000,
        "twitter_followers": 42000,
        "engagement_rate": 2.9,
        "recruiting_rank": 12,
    },
    {
        "name": "Keon Keeley",
        "school": "Notre Dame",
        "sport": "football",
        "position": "EDGE",
        "year": "Junior",
        "conference": "ACC",
        "instagram_followers": 180000,
        "twitter_followers": 65000,
        "engagement_rate": 3.4,
        "recruiting_rank": 3,
    },
]

async def refresh_athlete(db, athlete_data: dict) -> dict:
    """Score one athlete and upsert into the database."""
    from sqlalchemy import select

    athlete_id = athlete_data["id"]

    # Get prior score for delta calculation
    result = await db.execute(select(Athlete).where(Athlete.id == athlete_id))
    existing = result.scalar_one_or_none()
    old_score = existing.current_score if existing else None

    # Call Claude to infer component scores
    print(f"  Scoring {athlete_data['name']}...", flush=True)
    scores = infer_athlete_scores(athlete_data)
    print(f"    -> social={scores['social_score']}, athletic={scores['athletic_score']}, school={scores['school_score']}, position={scores['position_score']}")

    # Calculate composite and dollar value
    composite = calculate_nil_score(
        social_score=scores["social_score"],
        athletic_score=scores["athletic_score"],
        school_score=scores["school_score"],
        position_score=scores["position_score"],
    )
    dollar_score = composite_to_dollars(composite)
    delta = compute_score_delta(old_score, dollar_score)

    print(f"    -> NIL value: ${dollar_score:,.0f} ({delta:+.2f}%)")

    # Upsert athlete record
    if existing:
        existing.current_score = dollar_score
        existing.score_change_pct = delta
        existing.athletic_score = scores["athletic_score"]
        existing.school_market_score = scores["school_score"]
        existing.position_demand_score = scores["position_score"]
        existing.instagram_followers = athlete_data.get("instagram_followers", 0)
        existing.twitter_followers = athlete_data.get("twitter_followers", 0)
        existing.engagement_rate = athlete_data.get("engagement_rate", 0.0)
    else:
        new_athlete = Athlete(
            id=athlete_id,
            name=athlete_data["name"],
            school=athlete_data["school"],
            conference=athlete_data.get("conference"),
            sport=athlete_data["sport"],
            position=athlete_data.get("position"),
            year=athlete_data.get("year"),
            instagram_followers=athlete_data.get("instagram_followers", 0),
            twitter_followers=athlete_data.get("twitter_followers", 0),
            engagement_rate=athlete_data.get("engagement_rate", 0.0),
            recruiting_rank=athlete_data.get("recruiting_rank"),
            athletic_score=scores["athletic_score"],
            school_market_score=scores["school_score"],
            position_demand_score=scores["position_score"],
            current_score=dollar_score,
            score_change_pct=0.0,
        )
        db.add(new_athlete)

    # Always write score history
    history = ScoreHistory(
        athlete_id=athlete_id,
        score=dollar_score,
        social_component=scores["social_score"],
        athletic_component=scores["athletic_score"],
        school_component=scores["school_score"],
        position_component=scores["position_score"],
        week_date=date.today(),
    )
    db.add(history)

    return {"name": athlete_data["name"], "score": dollar_score, "delta": delta}

async def run():
    """Main pipeline entry point."""
    from backend.db.connection import AsyncSessionLocal

    if AsyncSessionLocal is None:
        print("ERROR: DATABASE_URL not configured.", file=sys.stderr)
        sys.exit(1)

    print(f"NIL Institute — Weekly Refresh ({date.today()})")
    print(f"Processing {len(SEED_ATHLETES)} athletes...\n")

    results = []
    async with AsyncSessionLocal() as db:
        for raw in SEED_ATHLETES:
            try:
                async with db.begin_nested():
                    normalized = normalize_athlete_data(raw)
                    result = await refresh_athlete(db, normalized)
                results.append(result)
            except Exception as e:
                print(f"  ERROR processing {raw.get('name', '?')}: {e}", file=sys.stderr)

        await db.commit()

    print(f"\nRefresh complete -- {len(results)}/{len(SEED_ATHLETES)} athletes updated.")
    print("\nTop NIL values this week:")
    for r in sorted(results, key=lambda x: x["score"], reverse=True):
        print(f"  {r['name']}: ${r['score']:,.0f} ({r['delta']:+.2f}%)")

if __name__ == "__main__":
    asyncio.run(run())
