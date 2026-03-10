from fastapi import APIRouter, HTTPException
from sqlalchemy import select, or_, func
from backend.db.connection import AsyncSessionLocal
from backend.db.models import Athlete, ScoreHistory

router = APIRouter(prefix="/api")

@router.get("/athletes/{athlete_id}")
async def get_athlete(athlete_id: str):
    if AsyncSessionLocal is None:
        raise HTTPException(status_code=404, detail="Athlete not found")

    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Athlete).where(Athlete.id == athlete_id))
            athlete = result.scalar_one_or_none()
            if not athlete:
                raise HTTPException(status_code=404, detail="Athlete not found")

            history_result = await db.execute(
                select(ScoreHistory)
                .where(ScoreHistory.athlete_id == athlete_id)
                .order_by(ScoreHistory.week_date)
            )
            history = history_result.scalars().all()
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Athlete not found")

    return {
        "id": athlete.id,
        "name": athlete.name,
        "school": athlete.school,
        "conference": athlete.conference,
        "sport": athlete.sport,
        "position": athlete.position,
        "year": athlete.year,
        "current_score": athlete.current_score,
        "score_change_pct": athlete.score_change_pct,
        "components": {
            "social": athlete.instagram_followers,
            "athletic": athlete.athletic_score,
            "school": athlete.school_market_score,
            "position": athlete.position_demand_score,
        },
        "history": [
            {"date": str(h.week_date), "score": h.score}
            for h in history
        ],
    }

@router.get("/athletes")
async def search_athletes(q: str):
    if AsyncSessionLocal is None:
        return {"athletes": []}

    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Athlete)
                .where(
                    or_(
                        func.lower(Athlete.name).contains(q.lower()),
                        func.lower(Athlete.school).contains(q.lower()),
                    )
                )
                .limit(20)
            )
            athletes = result.scalars().all()
    except Exception:
        return {"athletes": []}

    return {
        "athletes": [
            {
                "id": a.id,
                "name": a.name,
                "school": a.school,
                "sport": a.sport,
                "current_score": a.current_score,
            }
            for a in athletes
        ]
    }
