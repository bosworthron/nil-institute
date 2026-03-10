from fastapi import APIRouter, Query
from sqlalchemy import select, desc
from backend.db.connection import AsyncSessionLocal
from backend.db.models import Athlete

router = APIRouter(prefix="/api")

@router.get("/leaderboard")
async def get_leaderboard(
    sport: str = Query("football"),
    conference: str = Query(None),
    school: str = Query(None),
    limit: int = Query(100, le=500),
):
    if AsyncSessionLocal is None:
        return {"athletes": []}

    try:
        async with AsyncSessionLocal() as db:
            query = (
                select(Athlete)
                .where(Athlete.sport == sport)
                .order_by(desc(Athlete.current_score))
            )
            if conference:
                query = query.where(Athlete.conference == conference)
            if school:
                query = query.where(Athlete.school == school)
            query = query.limit(limit)

            result = await db.execute(query)
            athletes = result.scalars().all()
    except Exception:
        return {"athletes": []}

    return {
        "athletes": [
            {
                "id": a.id,
                "name": a.name,
                "school": a.school,
                "conference": a.conference,
                "sport": a.sport,
                "position": a.position,
                "current_score": a.current_score,
                "score_change_pct": a.score_change_pct,
            }
            for a in athletes
        ]
    }
