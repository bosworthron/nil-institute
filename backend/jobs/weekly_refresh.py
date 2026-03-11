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
    # ── FOOTBALL ──────────────────────────────────────────────
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
        "name": "Dillon Gabriel",
        "school": "Oregon",
        "sport": "football",
        "position": "QB",
        "year": "Senior",
        "conference": "Big Ten",
        "instagram_followers": 210000,
        "twitter_followers": 95000,
        "engagement_rate": 3.1,
        "recruiting_rank": 8,
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
    {
        "name": "Tetairoa McMillan",
        "school": "Arizona",
        "sport": "football",
        "position": "WR",
        "year": "Junior",
        "conference": "Big 12",
        "instagram_followers": 155000,
        "twitter_followers": 58000,
        "engagement_rate": 3.2,
        "recruiting_rank": 5,
    },
    {
        "name": "Dylan Raiola",
        "school": "Nebraska",
        "sport": "football",
        "position": "QB",
        "year": "Freshman",
        "conference": "Big Ten",
        "instagram_followers": 320000,
        "twitter_followers": 140000,
        "engagement_rate": 4.8,
        "recruiting_rank": 1,
    },
    {
        "name": "Luther Burden III",
        "school": "Missouri",
        "sport": "football",
        "position": "WR",
        "year": "Junior",
        "conference": "SEC",
        "instagram_followers": 190000,
        "twitter_followers": 72000,
        "engagement_rate": 3.6,
        "recruiting_rank": 4,
    },
    {
        "name": "Ashton Jeanty",
        "school": "Boise State",
        "sport": "football",
        "position": "RB",
        "year": "Junior",
        "conference": "Mountain West",
        "instagram_followers": 145000,
        "twitter_followers": 52000,
        "engagement_rate": 3.9,
        "recruiting_rank": 7,
    },
    {
        "name": "Will Johnson",
        "school": "Michigan",
        "sport": "football",
        "position": "CB",
        "year": "Junior",
        "conference": "Big Ten",
        "instagram_followers": 125000,
        "twitter_followers": 48000,
        "engagement_rate": 2.8,
        "recruiting_rank": 6,
    },
    {
        "name": "James Pearce Jr.",
        "school": "Tennessee",
        "sport": "football",
        "position": "EDGE",
        "year": "Sophomore",
        "conference": "SEC",
        "instagram_followers": 98000,
        "twitter_followers": 38000,
        "engagement_rate": 2.9,
        "recruiting_rank": 9,
    },
    {
        "name": "Deion Sanders Jr.",
        "school": "Colorado",
        "sport": "football",
        "position": "WR",
        "year": "Senior",
        "conference": "Big 12",
        "instagram_followers": 420000,
        "twitter_followers": 185000,
        "engagement_rate": 5.2,
        "recruiting_rank": 15,
    },
    {
        "name": "Harold Perkins Jr.",
        "school": "LSU",
        "sport": "football",
        "position": "LB",
        "year": "Sophomore",
        "conference": "SEC",
        "instagram_followers": 88000,
        "twitter_followers": 34000,
        "engagement_rate": 2.7,
        "recruiting_rank": 10,
    },
    {
        "name": "Nico Iamaleava",
        "school": "Tennessee",
        "sport": "football",
        "position": "QB",
        "year": "Sophomore",
        "conference": "SEC",
        "instagram_followers": 175000,
        "twitter_followers": 68000,
        "engagement_rate": 3.3,
        "recruiting_rank": 2,
    },
    {
        "name": "Kelvin Banks Jr.",
        "school": "Texas",
        "sport": "football",
        "position": "OT",
        "year": "Junior",
        "conference": "SEC",
        "instagram_followers": 62000,
        "twitter_followers": 24000,
        "engagement_rate": 2.4,
        "recruiting_rank": 13,
    },
    {
        "name": "Jeremiah Smith",
        "school": "Ohio State",
        "sport": "football",
        "position": "WR",
        "year": "Freshman",
        "conference": "Big Ten",
        "instagram_followers": 285000,
        "twitter_followers": 118000,
        "engagement_rate": 4.6,
        "recruiting_rank": 1,
    },
    {
        "name": "Mason Graham",
        "school": "Michigan",
        "sport": "football",
        "position": "DT",
        "year": "Junior",
        "conference": "Big Ten",
        "instagram_followers": 78000,
        "twitter_followers": 30000,
        "engagement_rate": 2.5,
        "recruiting_rank": 16,
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
        "name": "Oluwafemi Oladejo",
        "school": "UCLA",
        "sport": "football",
        "position": "EDGE",
        "year": "Senior",
        "conference": "Big Ten",
        "instagram_followers": 55000,
        "twitter_followers": 22000,
        "engagement_rate": 2.3,
        "recruiting_rank": 18,
    },
    {
        "name": "Emeka Egbuka",
        "school": "Ohio State",
        "sport": "football",
        "position": "WR",
        "year": "Senior",
        "conference": "Big Ten",
        "instagram_followers": 118000,
        "twitter_followers": 46000,
        "engagement_rate": 3.0,
        "recruiting_rank": 17,
    },
    {
        "name": "Caleb Downs",
        "school": "Ohio State",
        "sport": "football",
        "position": "S",
        "year": "Sophomore",
        "conference": "Big Ten",
        "instagram_followers": 92000,
        "twitter_followers": 36000,
        "engagement_rate": 2.6,
        "recruiting_rank": 19,
    },
    {
        "name": "Abdul Carter",
        "school": "Penn State",
        "sport": "football",
        "position": "EDGE",
        "year": "Junior",
        "conference": "Big Ten",
        "instagram_followers": 82000,
        "twitter_followers": 32000,
        "engagement_rate": 2.7,
        "recruiting_rank": 20,
    },
    # ── BASKETBALL ────────────────────────────────────────────
    {
        "name": "Cooper Flagg",
        "school": "Duke",
        "sport": "mens_basketball",
        "position": "SF",
        "year": "Freshman",
        "conference": "ACC",
        "instagram_followers": 750000,
        "twitter_followers": 280000,
        "engagement_rate": 5.1,
        "recruiting_rank": 1,
    },
    {
        "name": "Ace Bailey",
        "school": "Rutgers",
        "sport": "mens_basketball",
        "position": "SF",
        "year": "Freshman",
        "conference": "Big Ten",
        "instagram_followers": 320000,
        "twitter_followers": 125000,
        "engagement_rate": 4.3,
        "recruiting_rank": 2,
    },
    {
        "name": "Dylan Harper",
        "school": "Rutgers",
        "sport": "mens_basketball",
        "position": "PG",
        "year": "Freshman",
        "conference": "Big Ten",
        "instagram_followers": 285000,
        "twitter_followers": 110000,
        "engagement_rate": 4.1,
        "recruiting_rank": 3,
    },
    {
        "name": "VJ Edgecombe",
        "school": "Baylor",
        "sport": "mens_basketball",
        "position": "SG",
        "year": "Freshman",
        "conference": "Big 12",
        "instagram_followers": 195000,
        "twitter_followers": 78000,
        "engagement_rate": 3.8,
        "recruiting_rank": 4,
    },
    {
        "name": "Tre Johnson",
        "school": "Texas",
        "sport": "mens_basketball",
        "position": "SG",
        "year": "Freshman",
        "conference": "SEC",
        "instagram_followers": 165000,
        "twitter_followers": 64000,
        "engagement_rate": 3.5,
        "recruiting_rank": 5,
    },
    {
        "name": "Kon Knueppel",
        "school": "Duke",
        "sport": "mens_basketball",
        "position": "SG",
        "year": "Freshman",
        "conference": "ACC",
        "instagram_followers": 145000,
        "twitter_followers": 55000,
        "engagement_rate": 3.2,
        "recruiting_rank": 6,
    },
    {
        "name": "Khaman Maluach",
        "school": "Duke",
        "sport": "mens_basketball",
        "position": "C",
        "year": "Freshman",
        "conference": "ACC",
        "instagram_followers": 128000,
        "twitter_followers": 48000,
        "engagement_rate": 3.0,
        "recruiting_rank": 7,
    },
    {
        "name": "Kasparas Jakucionis",
        "school": "Illinois",
        "sport": "mens_basketball",
        "position": "PG",
        "year": "Freshman",
        "conference": "Big Ten",
        "instagram_followers": 98000,
        "twitter_followers": 38000,
        "engagement_rate": 2.8,
        "recruiting_rank": 8,
    },
    {
        "name": "Boogie Fland",
        "school": "Arkansas",
        "sport": "mens_basketball",
        "position": "PG",
        "year": "Freshman",
        "conference": "SEC",
        "instagram_followers": 112000,
        "twitter_followers": 44000,
        "engagement_rate": 2.9,
        "recruiting_rank": 10,
    },
    {
        "name": "Airious Bailey",
        "school": "Georgia",
        "sport": "mens_basketball",
        "position": "PG",
        "year": "Freshman",
        "conference": "SEC",
        "instagram_followers": 88000,
        "twitter_followers": 34000,
        "engagement_rate": 2.7,
        "recruiting_rank": 11,
    },
    {
        "name": "Derik Queen",
        "school": "Maryland",
        "sport": "mens_basketball",
        "position": "C",
        "year": "Freshman",
        "conference": "Big Ten",
        "instagram_followers": 75000,
        "twitter_followers": 29000,
        "engagement_rate": 2.5,
        "recruiting_rank": 12,
    },
    {
        "name": "Liam McNeeley",
        "school": "UConn",
        "sport": "mens_basketball",
        "position": "SF",
        "year": "Freshman",
        "conference": "Big East",
        "instagram_followers": 82000,
        "twitter_followers": 32000,
        "engagement_rate": 2.6,
        "recruiting_rank": 13,
    },
    {
        "name": "Jeremiah Fears",
        "school": "Oklahoma",
        "sport": "mens_basketball",
        "position": "PG",
        "year": "Freshman",
        "conference": "SEC",
        "instagram_followers": 68000,
        "twitter_followers": 26000,
        "engagement_rate": 2.4,
        "recruiting_rank": 14,
    },
    {
        "name": "RJ Luis Jr.",
        "school": "St. John's",
        "sport": "mens_basketball",
        "position": "SF",
        "year": "Junior",
        "conference": "Big East",
        "instagram_followers": 72000,
        "twitter_followers": 28000,
        "engagement_rate": 2.5,
        "recruiting_rank": 15,
    },
    {
        "name": "Chaz Lanier",
        "school": "Tennessee",
        "sport": "mens_basketball",
        "position": "SG",
        "year": "Senior",
        "conference": "SEC",
        "instagram_followers": 58000,
        "twitter_followers": 22000,
        "engagement_rate": 2.3,
        "recruiting_rank": 16,
    },
    {
        "name": "Walter Clayton Jr.",
        "school": "Florida",
        "sport": "mens_basketball",
        "position": "PG",
        "year": "Senior",
        "conference": "SEC",
        "instagram_followers": 62000,
        "twitter_followers": 24000,
        "engagement_rate": 2.4,
        "recruiting_rank": 17,
    },
    {
        "name": "Hunter Dickinson",
        "school": "Kansas",
        "sport": "mens_basketball",
        "position": "C",
        "year": "Senior",
        "conference": "Big 12",
        "instagram_followers": 195000,
        "twitter_followers": 78000,
        "engagement_rate": 3.7,
        "recruiting_rank": 18,
    },
    {
        "name": "JuJu Watkins",
        "school": "USC",
        "sport": "womens_basketball",
        "position": "SG",
        "year": "Sophomore",
        "conference": "Big Ten",
        "instagram_followers": 980000,
        "twitter_followers": 320000,
        "engagement_rate": 5.8,
        "recruiting_rank": 1,
    },
    {
        "name": "Flau'jae Johnson",
        "school": "LSU",
        "sport": "womens_basketball",
        "position": "SG",
        "year": "Junior",
        "conference": "SEC",
        "instagram_followers": 1450000,
        "twitter_followers": 480000,
        "engagement_rate": 6.4,
        "recruiting_rank": 3,
    },
    {
        "name": "Olivia Miles",
        "school": "Notre Dame",
        "sport": "womens_basketball",
        "position": "PG",
        "year": "Junior",
        "conference": "ACC",
        "instagram_followers": 420000,
        "twitter_followers": 145000,
        "engagement_rate": 4.9,
        "recruiting_rank": 2,
    },
    {
        "name": "Hannah Hidalgo",
        "school": "Notre Dame",
        "sport": "womens_basketball",
        "position": "PG",
        "year": "Junior",
        "conference": "ACC",
        "instagram_followers": 185000,
        "twitter_followers": 62000,
        "engagement_rate": 3.8,
        "recruiting_rank": 5,
    },
    {
        "name": "Sonia Citron",
        "school": "Notre Dame",
        "sport": "womens_basketball",
        "position": "SG",
        "year": "Junior",
        "conference": "ACC",
        "instagram_followers": 145000,
        "twitter_followers": 48000,
        "engagement_rate": 3.4,
        "recruiting_rank": 6,
    },
    {
        "name": "Mark Sears",
        "school": "Alabama",
        "sport": "mens_basketball",
        "position": "PG",
        "year": "Senior",
        "conference": "SEC",
        "instagram_followers": 55000,
        "twitter_followers": 21000,
        "engagement_rate": 2.2,
        "recruiting_rank": 20,
    },
    {
        "name": "Johni Broome",
        "school": "Auburn",
        "sport": "mens_basketball",
        "position": "C",
        "year": "Senior",
        "conference": "SEC",
        "instagram_followers": 48000,
        "twitter_followers": 18000,
        "engagement_rate": 2.1,
        "recruiting_rank": 21,
    },
    {
        "name": "John Tonje",
        "school": "Wisconsin",
        "sport": "mens_basketball",
        "position": "SG",
        "year": "Senior",
        "conference": "Big Ten",
        "instagram_followers": 42000,
        "twitter_followers": 16000,
        "engagement_rate": 2.0,
        "recruiting_rank": 22,
    },
    {
        "name": "Miles Byrd",
        "school": "San Diego State",
        "sport": "mens_basketball",
        "position": "SF",
        "year": "Junior",
        "conference": "Mountain West",
        "instagram_followers": 38000,
        "twitter_followers": 15000,
        "engagement_rate": 2.0,
        "recruiting_rank": 23,
    },
    {
        "name": "Zach Edey",
        "school": "Purdue",
        "sport": "mens_basketball",
        "position": "C",
        "year": "Senior",
        "conference": "Big Ten",
        "instagram_followers": 225000,
        "twitter_followers": 88000,
        "engagement_rate": 3.9,
        "recruiting_rank": 5,
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
