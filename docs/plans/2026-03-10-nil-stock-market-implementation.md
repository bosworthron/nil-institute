# NIL Stock Market Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a public-facing NIL valuation platform where college athletes are displayed like stock tickers with weekly-refreshed composite scores.

**Architecture:** FastAPI backend with a weekly scraping + Claude AI scoring pipeline writing to Neon Postgres, cached in Redis, served to a Next.js frontend with Robinhood-style UI. Freemium gating via Clerk with ad placements on free tier.

**Tech Stack:** Next.js 14, Tailwind CSS, FastAPI, Python 3.12, Neon (Postgres), Redis, Playwright, BeautifulSoup, Claude API (claude-sonnet-4-6), Clerk, Vercel, Railway

---

## Repo Structure

```
NIL_tracker/
├── frontend/          # Next.js app
├── backend/           # FastAPI app
│   ├── scrapers/
│   ├── scoring/
│   ├── api/
│   └── tests/
├── docs/
│   └── plans/
└── docker-compose.yml
```

---

### Task 1: Project Scaffolding

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/main.py`
- Create: `frontend/` (Next.js scaffold)
- Create: `docker-compose.yml`

**Step 1: Initialize backend**

```bash
cd /c/Users/boswo/claudecode/NIL_tracker
mkdir -p backend/scrapers backend/scoring backend/api backend/tests
cd backend
python -m venv venv
source venv/Scripts/activate  # Windows
pip install fastapi uvicorn sqlalchemy asyncpg neon-python redis playwright beautifulsoup4 httpx pytest pytest-asyncio anthropic python-dotenv
pip freeze > requirements.txt
```

**Step 2: Create backend entry point**

Create `backend/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="NIL Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}
```

**Step 3: Run and verify**

```bash
cd backend
uvicorn main:app --reload
```
Expected: `Uvicorn running on http://127.0.0.1:8000`
Visit `http://localhost:8000/health` → `{"status": "ok"}`

**Step 4: Initialize Next.js frontend**

```bash
cd /c/Users/boswo/claudecode/NIL_tracker
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir
```

**Step 5: Verify frontend**

```bash
cd frontend && npm run dev
```
Expected: App running on `http://localhost:3000`

**Step 6: Create .env files**

Create `backend/.env`:
```
DATABASE_URL=postgresql://...  # Neon connection string
REDIS_URL=redis://localhost:6379
ANTHROPIC_API_KEY=sk-ant-...
```

Create `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_...
CLERK_SECRET_KEY=sk_...
```

**Step 7: Commit**

```bash
cd /c/Users/boswo/claudecode/NIL_tracker
git init
git add .
git commit -m "feat: initial project scaffold — FastAPI backend + Next.js frontend"
```

---

### Task 2: Database Schema

**Files:**
- Create: `backend/db/schema.sql`
- Create: `backend/db/models.py`
- Create: `backend/db/connection.py`
- Test: `backend/tests/test_models.py`

**Step 1: Write the failing test**

Create `backend/tests/test_models.py`:
```python
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
```

**Step 2: Run test to verify it fails**

```bash
cd backend && pytest tests/test_models.py -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'backend.db'`

**Step 3: Create database schema**

Create `backend/db/schema.sql`:
```sql
CREATE TABLE IF NOT EXISTS athletes (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    school VARCHAR NOT NULL,
    conference VARCHAR,
    sport VARCHAR NOT NULL,
    position VARCHAR,
    year VARCHAR,
    instagram_handle VARCHAR,
    twitter_handle VARCHAR,
    tiktok_handle VARCHAR,
    instagram_followers INTEGER DEFAULT 0,
    twitter_followers INTEGER DEFAULT 0,
    engagement_rate FLOAT DEFAULT 0.0,
    recruiting_rank INTEGER,
    athletic_score FLOAT DEFAULT 0.0,
    school_market_score FLOAT DEFAULT 0.0,
    position_demand_score FLOAT DEFAULT 0.0,
    current_score FLOAT DEFAULT 0.0,
    score_change_pct FLOAT DEFAULT 0.0,
    last_updated TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS score_history (
    id SERIAL PRIMARY KEY,
    athlete_id VARCHAR REFERENCES athletes(id),
    score FLOAT NOT NULL,
    social_component FLOAT,
    athletic_component FLOAT,
    school_component FLOAT,
    position_component FLOAT,
    week_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_athletes_sport ON athletes(sport);
CREATE INDEX IF NOT EXISTS idx_athletes_school ON athletes(school);
CREATE INDEX IF NOT EXISTS idx_athletes_score ON athletes(current_score DESC);
CREATE INDEX IF NOT EXISTS idx_score_history_athlete ON score_history(athlete_id);
```

**Step 4: Create SQLAlchemy models**

Create `backend/db/models.py`:
```python
from sqlalchemy import Column, String, Float, Integer, Date, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Athlete(Base):
    __tablename__ = "athletes"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    school = Column(String, nullable=False)
    conference = Column(String)
    sport = Column(String, nullable=False)
    position = Column(String)
    year = Column(String)
    instagram_handle = Column(String)
    twitter_handle = Column(String)
    tiktok_handle = Column(String)
    instagram_followers = Column(Integer, default=0)
    twitter_followers = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    recruiting_rank = Column(Integer)
    athletic_score = Column(Float, default=0.0)
    school_market_score = Column(Float, default=0.0)
    position_demand_score = Column(Float, default=0.0)
    current_score = Column(Float, default=0.0)
    score_change_pct = Column(Float, default=0.0)
    last_updated = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())

class ScoreHistory(Base):
    __tablename__ = "score_history"
    id = Column(Integer, primary_key=True, autoincrement=True)
    athlete_id = Column(String, ForeignKey("athletes.id"))
    score = Column(Float, nullable=False)
    social_component = Column(Float)
    athletic_component = Column(Float)
    school_component = Column(Float)
    position_component = Column(Float)
    week_date = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
```

**Step 5: Create database connection**

Create `backend/db/connection.py`:
```python
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL").replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

Create `backend/db/__init__.py` (empty)

**Step 6: Run test to verify it passes**

```bash
cd backend && pytest tests/test_models.py -v
```
Expected: PASS

**Step 7: Apply schema to Neon**

```bash
# Get connection string from Neon dashboard
psql $DATABASE_URL -f db/schema.sql
```
Expected: `CREATE TABLE`, `CREATE INDEX` messages

**Step 8: Commit**

```bash
git add backend/db/ backend/tests/test_models.py
git commit -m "feat: database schema — athletes + score_history tables"
```

---

### Task 3: Scoring Engine

**Files:**
- Create: `backend/scoring/engine.py`
- Create: `backend/scoring/claude_client.py`
- Test: `backend/tests/test_scoring.py`

**Step 1: Write the failing test**

Create `backend/tests/test_scoring.py`:
```python
import pytest
from backend.scoring.engine import calculate_nil_score, compute_score_delta

def test_composite_score_weights():
    score = calculate_nil_score(
        social_score=100.0,
        athletic_score=100.0,
        school_score=100.0,
        position_score=100.0,
    )
    assert score == 100.0

def test_composite_score_partial():
    score = calculate_nil_score(
        social_score=100.0,
        athletic_score=0.0,
        school_score=0.0,
        position_score=0.0,
    )
    assert score == 35.0  # 35% weight for social

def test_score_delta_positive():
    delta = compute_score_delta(old_score=800000, new_score=847000)
    assert round(delta, 2) == 5.88

def test_score_delta_negative():
    delta = compute_score_delta(old_score=847000, new_score=800000)
    assert round(delta, 2) == -5.55

def test_score_delta_no_previous():
    delta = compute_score_delta(old_score=None, new_score=847000)
    assert delta == 0.0
```

**Step 2: Run test to verify it fails**

```bash
pytest backend/tests/test_scoring.py -v
```
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Implement scoring engine**

Create `backend/scoring/engine.py`:
```python
from typing import Optional

WEIGHTS = {
    "social": 0.35,
    "athletic": 0.30,
    "school": 0.20,
    "position": 0.15,
}

# NIL score ceiling — top athletes approach this
MAX_NIL_VALUE = 5_000_000

def calculate_nil_score(
    social_score: float,
    athletic_score: float,
    school_score: float,
    position_score: float,
) -> float:
    """
    Returns a normalized composite score (0-100).
    Multiply by MAX_NIL_VALUE scaling factor to get dollar estimate.
    """
    composite = (
        social_score * WEIGHTS["social"]
        + athletic_score * WEIGHTS["athletic"]
        + school_score * WEIGHTS["school"]
        + position_score * WEIGHTS["position"]
    )
    return round(composite, 4)

def composite_to_dollars(composite_score: float) -> float:
    """Convert 0-100 composite score to estimated NIL dollar value."""
    # Exponential scaling: top athletes earn disproportionately more
    normalized = composite_score / 100.0
    dollar_value = MAX_NIL_VALUE * (normalized ** 2.2)
    return round(dollar_value, 0)

def compute_score_delta(old_score: Optional[float], new_score: float) -> float:
    """Returns % change between old and new score."""
    if old_score is None or old_score == 0:
        return 0.0
    delta = ((new_score - old_score) / old_score) * 100
    return round(delta, 2)
```

**Step 4: Run test to verify it passes**

```bash
pytest backend/tests/test_scoring.py -v
```
Expected: PASS — all 5 tests

**Step 5: Create Claude AI client for inference**

Create `backend/scoring/claude_client.py`:
```python
import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def infer_athlete_scores(athlete_data: dict) -> dict:
    """
    Uses Claude to fill in missing data and estimate component scores.
    Returns dict with social_score, athletic_score, school_score, position_score (each 0-100).
    """
    prompt = f"""You are an NIL valuation analyst. Given this college athlete's data, estimate four component scores (0-100 each):

Athlete data:
{json.dumps(athlete_data, indent=2)}

Scoring criteria:
- social_score (0-100): Based on follower counts, engagement rate, platform presence. 100 = Paige Bueckers / top 0.1%
- athletic_score (0-100): Based on recruiting rank, stats, draft projection, team success. 100 = #1 overall recruit / Heisman contender
- school_score (0-100): Based on school's media market size, program prestige, conference. 100 = Alabama/Ohio State in top-10 media market
- position_score (0-100): Based on NIL demand for this position/sport combo. 100 = QB or PG with elite program

Return ONLY valid JSON:
{{"social_score": 0-100, "athletic_score": 0-100, "school_score": 0-100, "position_score": 0-100, "reasoning": "brief explanation"}}
"""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(response.content[0].text)
```

**Step 6: Commit**

```bash
git add backend/scoring/ backend/tests/test_scoring.py
git commit -m "feat: NIL composite scoring engine with Claude AI inference"
```

---

### Task 4: Scrapers

**Files:**
- Create: `backend/scrapers/espn.py`
- Create: `backend/scrapers/social.py`
- Create: `backend/scrapers/pipeline.py`
- Test: `backend/tests/test_scrapers.py`

**Step 1: Write the failing test**

Create `backend/tests/test_scrapers.py`:
```python
import pytest
from backend.scrapers.pipeline import normalize_athlete_data

def test_normalize_athlete_data_complete():
    raw = {
        "name": "John Smith",
        "school": "Alabama",
        "sport": "football",
        "position": "QB",
        "instagram_followers": 50000,
        "twitter_followers": 20000,
        "engagement_rate": 3.5,
    }
    result = normalize_athlete_data(raw)
    assert result["name"] == "John Smith"
    assert result["id"] == "john-smith-alabama-football"
    assert result["instagram_followers"] == 50000

def test_normalize_athlete_data_missing_social():
    raw = {
        "name": "Jane Doe",
        "school": "Stanford",
        "sport": "basketball",
        "position": "PG",
    }
    result = normalize_athlete_data(raw)
    assert result["instagram_followers"] == 0
    assert result["engagement_rate"] == 0.0
```

**Step 2: Run test to verify it fails**

```bash
pytest backend/tests/test_scrapers.py -v
```
Expected: FAIL

**Step 3: Implement pipeline normalizer**

Create `backend/scrapers/pipeline.py`:
```python
import re
from typing import Optional

def normalize_athlete_data(raw: dict) -> dict:
    """Normalize raw scraped data into consistent athlete record."""
    name = raw.get("name", "").strip()
    school = raw.get("school", "").strip()
    sport = raw.get("sport", "").strip()

    # Generate stable ID from name + school + sport
    id_parts = f"{name}-{school}-{sport}".lower()
    athlete_id = re.sub(r"[^a-z0-9]+", "-", id_parts).strip("-")

    return {
        "id": athlete_id,
        "name": name,
        "school": school,
        "conference": raw.get("conference"),
        "sport": sport,
        "position": raw.get("position"),
        "year": raw.get("year"),
        "instagram_handle": raw.get("instagram_handle"),
        "twitter_handle": raw.get("twitter_handle"),
        "tiktok_handle": raw.get("tiktok_handle"),
        "instagram_followers": raw.get("instagram_followers", 0),
        "twitter_followers": raw.get("twitter_followers", 0),
        "engagement_rate": raw.get("engagement_rate", 0.0),
        "recruiting_rank": raw.get("recruiting_rank"),
    }
```

**Step 4: Implement ESPN scraper (basic)**

Create `backend/scrapers/espn.py`:
```python
import httpx
from bs4 import BeautifulSoup
from typing import List

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; NILTracker/1.0)"
}

async def scrape_espn_roster(school_slug: str, sport: str = "football") -> List[dict]:
    """
    Scrape basic roster data from ESPN.
    school_slug: e.g. 'alabama', 'ohio-state'
    """
    url = f"https://www.espn.com/college-{sport}/team/roster/_/id/{school_slug}"
    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True) as client:
        resp = await client.get(url, timeout=15)
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    athletes = []

    rows = soup.select("table.Table tr.Table__TR")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 4:
            continue
        athletes.append({
            "name": cells[1].get_text(strip=True) if len(cells) > 1 else "",
            "position": cells[2].get_text(strip=True) if len(cells) > 2 else "",
            "year": cells[4].get_text(strip=True) if len(cells) > 4 else "",
            "school": school_slug,
            "sport": sport,
        })

    return athletes
```

**Step 5: Implement social scraper stub**

Create `backend/scrapers/social.py`:
```python
"""
Social media scraping.
Phase 1: Returns estimated follower counts based on athlete profile data.
Phase 2: Integrate with social media APIs or scraping services.
"""
from typing import Optional

def estimate_social_presence(athlete_name: str, school: str, sport: str, position: str) -> dict:
    """
    Phase 1: Claude AI estimates social presence based on athlete context.
    Returns estimated follower counts and engagement rate.
    """
    # Placeholder — replaced by Claude inference in scoring pipeline
    return {
        "instagram_followers": 0,
        "twitter_followers": 0,
        "tiktok_followers": 0,
        "engagement_rate": 0.0,
        "social_estimated": True,
    }
```

**Step 6: Run tests to verify they pass**

```bash
pytest backend/tests/test_scrapers.py -v
```
Expected: PASS

**Step 7: Commit**

```bash
git add backend/scrapers/ backend/tests/test_scrapers.py
git commit -m "feat: scraping pipeline — ESPN roster scraper + data normalizer"
```

---

### Task 5: API Endpoints

**Files:**
- Create: `backend/api/athletes.py`
- Create: `backend/api/leaderboard.py`
- Modify: `backend/main.py`
- Test: `backend/tests/test_api.py`

**Step 1: Write the failing tests**

Create `backend/tests/test_api.py`:
```python
import pytest
from httpx import AsyncClient
from backend.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_leaderboard_endpoint_exists():
    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.get("/api/leaderboard?sport=football&limit=10")
    assert resp.status_code == 200
    assert "athletes" in resp.json()

@pytest.mark.asyncio
async def test_athlete_endpoint_exists():
    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.get("/api/athletes/john-smith-alabama-football")
    assert resp.status_code in [200, 404]  # 404 ok if no data yet
```

**Step 2: Run test to verify it fails**

```bash
pytest backend/tests/test_api.py -v
```
Expected: FAIL on leaderboard + athlete endpoints

**Step 3: Create leaderboard endpoint**

Create `backend/api/leaderboard.py`:
```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from backend.db.connection import get_db
from backend.db.models import Athlete

router = APIRouter(prefix="/api")

@router.get("/leaderboard")
async def get_leaderboard(
    sport: str = Query("football"),
    conference: str = Query(None),
    school: str = Query(None),
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db),
):
    query = select(Athlete).where(Athlete.sport == sport).order_by(desc(Athlete.current_score))
    if conference:
        query = query.where(Athlete.conference == conference)
    if school:
        query = query.where(Athlete.school == school)
    query = query.limit(limit)

    result = await db.execute(query)
    athletes = result.scalars().all()

    return {
        "athletes": [
            {
                "id": a.id,
                "name": a.name,
                "school": a.school,
                "sport": a.sport,
                "position": a.position,
                "current_score": a.current_score,
                "score_change_pct": a.score_change_pct,
            }
            for a in athletes
        ]
    }
```

**Step 4: Create athlete detail endpoint**

Create `backend/api/athletes.py`:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.db.connection import get_db
from backend.db.models import Athlete, ScoreHistory

router = APIRouter(prefix="/api")

@router.get("/athletes/{athlete_id}")
async def get_athlete(athlete_id: str, db: AsyncSession = Depends(get_db)):
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
async def search_athletes(q: str, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import or_, func
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
    return {"athletes": [{"id": a.id, "name": a.name, "school": a.school, "sport": a.sport, "current_score": a.current_score} for a in athletes]}
```

**Step 5: Register routes in main.py**

Modify `backend/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.athletes import router as athletes_router
from backend.api.leaderboard import router as leaderboard_router

app = FastAPI(title="NIL Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(athletes_router)
app.include_router(leaderboard_router)

@app.get("/health")
def health():
    return {"status": "ok"}
```

**Step 6: Run tests to verify they pass**

```bash
pytest backend/tests/test_api.py -v
```
Expected: PASS — all 3 tests

**Step 7: Commit**

```bash
git add backend/api/ backend/main.py backend/tests/test_api.py
git commit -m "feat: REST API — leaderboard, athlete detail, and search endpoints"
```

---

### Task 6: Frontend — Design System & Layout

**Files:**
- Modify: `frontend/app/globals.css`
- Create: `frontend/components/layout/Navbar.tsx`
- Create: `frontend/components/ui/ScoreTicker.tsx`
- Create: `frontend/lib/api.ts`

**Step 1: Set up Robinhood-inspired color system**

Modify `frontend/app/globals.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --color-bg: #0a0a0a;
  --color-surface: #111111;
  --color-border: #1f1f1f;
  --color-text-primary: #ffffff;
  --color-text-secondary: #8a8a8a;
  --color-green: #00c805;
  --color-red: #ff5000;
  --color-gold: #f5c842;
}

body {
  background: var(--color-bg);
  color: var(--color-text-primary);
  font-family: 'Inter', sans-serif;
}
```

**Step 2: Create API client**

Create `frontend/lib/api.ts`:
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function getLeaderboard(sport = "football", limit = 100) {
  const res = await fetch(`${API_URL}/api/leaderboard?sport=${sport}&limit=${limit}`);
  if (!res.ok) throw new Error("Failed to fetch leaderboard");
  return res.json();
}

export async function getAthlete(athleteId: string) {
  const res = await fetch(`${API_URL}/api/athletes/${athleteId}`);
  if (!res.ok) throw new Error("Athlete not found");
  return res.json();
}

export async function searchAthletes(query: string) {
  const res = await fetch(`${API_URL}/api/athletes?q=${encodeURIComponent(query)}`);
  if (!res.ok) throw new Error("Search failed");
  return res.json();
}

export function formatNIL(score: number): string {
  if (score >= 1_000_000) return `$${(score / 1_000_000).toFixed(2)}M`;
  if (score >= 1_000) return `$${(score / 1_000).toFixed(0)}K`;
  return `$${score.toFixed(0)}`;
}
```

**Step 3: Create ScoreTicker component**

Create `frontend/components/ui/ScoreTicker.tsx`:
```tsx
interface ScoreTickerProps {
  score: number;
  changePct: number;
  size?: "sm" | "lg";
}

export function ScoreTicker({ score, changePct, size = "sm" }: ScoreTickerProps) {
  const isPositive = changePct >= 0;
  const arrow = isPositive ? "▲" : "▼";
  const color = isPositive ? "text-green-400" : "text-orange-500";
  const formatted = score >= 1_000_000
    ? `$${(score / 1_000_000).toFixed(2)}M`
    : `$${(score / 1_000).toFixed(0)}K`;

  return (
    <div className={size === "lg" ? "text-right" : "text-right"}>
      <div className={`font-bold tabular-nums ${size === "lg" ? "text-3xl" : "text-base"}`}>
        {formatted}
      </div>
      <div className={`text-sm font-medium tabular-nums ${color}`}>
        {arrow} {Math.abs(changePct).toFixed(2)}%
      </div>
    </div>
  );
}
```

**Step 4: Create Navbar**

Create `frontend/components/layout/Navbar.tsx`:
```tsx
import Link from "next/link";

export function Navbar() {
  return (
    <nav className="border-b border-[#1f1f1f] bg-[#0a0a0a] px-6 py-4 flex items-center justify-between sticky top-0 z-50">
      <Link href="/" className="text-xl font-bold tracking-tight">
        NIL<span className="text-green-400">Track</span>
      </Link>
      <div className="flex items-center gap-6 text-sm text-[#8a8a8a]">
        <Link href="/leaderboard" className="hover:text-white transition-colors">Leaderboard</Link>
        <Link href="/search" className="hover:text-white transition-colors">Search</Link>
        <Link href="/upgrade" className="bg-white text-black px-3 py-1.5 rounded-full text-xs font-semibold hover:bg-gray-200 transition-colors">
          Go Pro
        </Link>
      </div>
    </nav>
  );
}
```

**Step 5: Commit**

```bash
git add frontend/
git commit -m "feat: frontend design system — dark theme, ScoreTicker, Navbar"
```

---

### Task 7: Frontend — Home & Leaderboard Pages

**Files:**
- Modify: `frontend/app/page.tsx`
- Create: `frontend/app/leaderboard/page.tsx`
- Create: `frontend/components/athletes/AthleteRow.tsx`

**Step 1: Create AthleteRow component**

Create `frontend/components/athletes/AthleteRow.tsx`:
```tsx
import Link from "next/link";
import { ScoreTicker } from "@/components/ui/ScoreTicker";

interface AthleteRowProps {
  rank: number;
  athlete: {
    id: string;
    name: string;
    school: string;
    position: string;
    sport: string;
    current_score: number;
    score_change_pct: number;
  };
}

export function AthleteRow({ rank, athlete }: AthleteRowProps) {
  return (
    <Link href={`/athletes/${athlete.id}`}>
      <div className="flex items-center gap-4 px-4 py-3 hover:bg-[#111111] transition-colors border-b border-[#1f1f1f] cursor-pointer">
        <span className="text-[#8a8a8a] text-sm w-8 tabular-nums">{rank}</span>
        <div className="flex-1 min-w-0">
          <div className="font-semibold text-sm truncate">{athlete.name}</div>
          <div className="text-[#8a8a8a] text-xs">{athlete.school} · {athlete.position}</div>
        </div>
        <ScoreTicker score={athlete.current_score} changePct={athlete.score_change_pct} />
      </div>
    </Link>
  );
}
```

**Step 2: Build Home page**

Modify `frontend/app/page.tsx`:
```tsx
import { Navbar } from "@/components/layout/Navbar";
import { AthleteRow } from "@/components/athletes/AthleteRow";
import { getLeaderboard } from "@/lib/api";

export default async function Home() {
  const data = await getLeaderboard("football", 20);
  const athletes = data.athletes || [];

  return (
    <main className="min-h-screen bg-[#0a0a0a]">
      <Navbar />
      <div className="max-w-2xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold mb-1">NIL Market</h1>
          <p className="text-[#8a8a8a] text-sm">Predicted NIL valuations for college athletes, updated weekly.</p>
        </div>

        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-[#8a8a8a] uppercase tracking-wider">Top Movers</h2>
          <span className="text-xs text-[#8a8a8a]">Football</span>
        </div>

        <div className="rounded-xl border border-[#1f1f1f] overflow-hidden">
          {athletes.length === 0 ? (
            <div className="p-8 text-center text-[#8a8a8a]">No data yet — pipeline running soon.</div>
          ) : (
            athletes.map((athlete: any, i: number) => (
              <AthleteRow key={athlete.id} rank={i + 1} athlete={athlete} />
            ))
          )}
        </div>
      </div>
    </main>
  );
}
```

**Step 3: Build Leaderboard page**

Create `frontend/app/leaderboard/page.tsx`:
```tsx
"use client";
import { useState, useEffect } from "react";
import { Navbar } from "@/components/layout/Navbar";
import { AthleteRow } from "@/components/athletes/AthleteRow";
import { getLeaderboard } from "@/lib/api";

const SPORTS = ["football", "basketball"];
const CONFERENCES = ["All", "SEC", "Big Ten", "Big 12", "ACC", "Pac-12"];

export default function LeaderboardPage() {
  const [sport, setSport] = useState("football");
  const [conference, setConference] = useState("All");
  const [athletes, setAthletes] = useState([]);

  useEffect(() => {
    getLeaderboard(sport, 100)
      .then((d) => setAthletes(d.athletes || []))
      .catch(console.error);
  }, [sport]);

  return (
    <main className="min-h-screen bg-[#0a0a0a]">
      <Navbar />
      <div className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">Leaderboard</h1>

        <div className="flex gap-2 mb-6 flex-wrap">
          {SPORTS.map((s) => (
            <button
              key={s}
              onClick={() => setSport(s)}
              className={`px-4 py-1.5 rounded-full text-sm font-medium capitalize transition-colors ${
                sport === s ? "bg-white text-black" : "bg-[#1f1f1f] text-[#8a8a8a] hover:text-white"
              }`}
            >
              {s}
            </button>
          ))}
        </div>

        <div className="rounded-xl border border-[#1f1f1f] overflow-hidden">
          {athletes.map((athlete: any, i: number) => (
            <AthleteRow key={athlete.id} rank={i + 1} athlete={athlete} />
          ))}
        </div>
      </div>
    </main>
  );
}
```

**Step 4: Commit**

```bash
git add frontend/
git commit -m "feat: home page + leaderboard with sport/conference filters"
```

---

### Task 8: Frontend — Athlete Detail Page

**Files:**
- Create: `frontend/app/athletes/[id]/page.tsx`
- Create: `frontend/components/athletes/ScoreChart.tsx`

**Step 1: Create score history chart**

Install chart library:
```bash
cd frontend && npm install recharts
```

Create `frontend/components/athletes/ScoreChart.tsx`:
```tsx
"use client";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

interface ScoreChartProps {
  data: { date: string; score: number }[];
}

export function ScoreChart({ data }: ScoreChartProps) {
  if (!data || data.length < 2) {
    return <div className="h-32 flex items-center justify-center text-[#8a8a8a] text-sm">Not enough history yet</div>;
  }

  return (
    <ResponsiveContainer width="100%" height={120}>
      <LineChart data={data}>
        <XAxis dataKey="date" hide />
        <YAxis hide domain={["auto", "auto"]} />
        <Tooltip
          contentStyle={{ background: "#111", border: "1px solid #1f1f1f", borderRadius: 8 }}
          labelStyle={{ color: "#8a8a8a", fontSize: 11 }}
          formatter={(val: number) => [`$${(val / 1000).toFixed(0)}K`, "NIL Value"]}
        />
        <Line type="monotone" dataKey="score" stroke="#00c805" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
```

**Step 2: Create athlete detail page**

Create `frontend/app/athletes/[id]/page.tsx`:
```tsx
import { Navbar } from "@/components/layout/Navbar";
import { ScoreTicker } from "@/components/ui/ScoreTicker";
import { ScoreChart } from "@/components/athletes/ScoreChart";
import { getAthlete } from "@/lib/api";
import { notFound } from "next/navigation";

export default async function AthletePage({ params }: { params: { id: string } }) {
  let athlete;
  try {
    athlete = await getAthlete(params.id);
  } catch {
    notFound();
  }

  return (
    <main className="min-h-screen bg-[#0a0a0a]">
      <Navbar />
      <div className="max-w-2xl mx-auto px-4 py-8">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">{athlete.name}</h1>
            <p className="text-[#8a8a8a] text-sm mt-1">
              {athlete.school} · {athlete.position} · {athlete.year}
            </p>
          </div>
          <ScoreTicker score={athlete.current_score} changePct={athlete.score_change_pct} size="lg" />
        </div>

        <div className="bg-[#111111] rounded-xl border border-[#1f1f1f] p-4 mb-4">
          <h3 className="text-xs text-[#8a8a8a] uppercase tracking-wider mb-3">NIL Value History</h3>
          <ScoreChart data={athlete.history} />
        </div>

        <div className="bg-[#111111] rounded-xl border border-[#1f1f1f] p-4">
          <h3 className="text-xs text-[#8a8a8a] uppercase tracking-wider mb-3">Score Breakdown</h3>
          <div className="space-y-2">
            {[
              { label: "Social Reach", value: athlete.components?.social, weight: "35%" },
              { label: "Athletic Performance", value: athlete.components?.athletic, weight: "30%" },
              { label: "School Market", value: athlete.components?.school, weight: "20%" },
              { label: "Position Demand", value: athlete.components?.position, weight: "15%" },
            ].map((item) => (
              <div key={item.label} className="flex items-center justify-between text-sm">
                <span className="text-[#8a8a8a]">{item.label}</span>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-[#555]">{item.weight}</span>
                  <span className="font-medium w-16 text-right tabular-nums">
                    {item.value?.toLocaleString() ?? "—"}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
```

**Step 3: Commit**

```bash
git add frontend/
git commit -m "feat: athlete detail page with score history chart and component breakdown"
```

---

### Task 9: Weekly Pipeline Job

**Files:**
- Create: `backend/jobs/weekly_refresh.py`

**Step 1: Create weekly scoring job**

Create `backend/jobs/weekly_refresh.py`:
```python
"""
Weekly NIL score refresh job.
Run manually or via cron: python -m backend.jobs.weekly_refresh
"""
import asyncio
from datetime import date
from backend.db.connection import AsyncSessionLocal
from backend.db.models import Athlete, ScoreHistory
from backend.scoring.engine import calculate_nil_score, composite_to_dollars, compute_score_delta
from backend.scoring.claude_client import infer_athlete_scores
from sqlalchemy import select

SEED_ATHLETES = [
    {"name": "Travis Hunter", "school": "Colorado", "sport": "football", "position": "WR/CB", "year": "Junior", "conference": "Big 12"},
    {"name": "Arch Manning", "school": "Texas", "sport": "football", "position": "QB", "year": "Sophomore", "conference": "SEC"},
    {"name": "Cooper Flagg", "school": "Duke", "sport": "basketball", "position": "SF", "year": "Freshman", "conference": "ACC"},
]

async def refresh_athlete(db, athlete_data: dict):
    athlete_id = athlete_data["id"]
    result = await db.execute(select(Athlete).where(Athlete.id == athlete_id))
    existing = result.scalar_one_or_none()
    old_score = existing.current_score if existing else None

    scores = infer_athlete_scores(athlete_data)

    composite = calculate_nil_score(
        social_score=scores["social_score"],
        athletic_score=scores["athletic_score"],
        school_score=scores["school_score"],
        position_score=scores["position_score"],
    )
    dollar_score = composite_to_dollars(composite)
    delta = compute_score_delta(old_score, dollar_score)

    if existing:
        existing.current_score = dollar_score
        existing.score_change_pct = delta
        existing.athletic_score = scores["athletic_score"]
        existing.school_market_score = scores["school_score"]
        existing.position_demand_score = scores["position_score"]
    else:
        athlete = Athlete(**athlete_data, current_score=dollar_score, score_change_pct=0.0)
        db.add(athlete)

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

async def run():
    from backend.scrapers.pipeline import normalize_athlete_data
    async with AsyncSessionLocal() as db:
        for raw in SEED_ATHLETES:
            normalized = normalize_athlete_data(raw)
            await refresh_athlete(db, normalized)
        await db.commit()
    print(f"Refreshed {len(SEED_ATHLETES)} athletes.")

if __name__ == "__main__":
    asyncio.run(run())
```

**Step 2: Run seed pipeline**

```bash
cd backend
python -m backend.jobs.weekly_refresh
```
Expected: `Refreshed 3 athletes.`

**Step 3: Verify data in database**

```bash
psql $DATABASE_URL -c "SELECT name, current_score, score_change_pct FROM athletes ORDER BY current_score DESC;"
```
Expected: 3 rows with dollar values

**Step 4: Commit**

```bash
git add backend/jobs/
git commit -m "feat: weekly NIL score refresh pipeline with seed athletes"
```

---

### Task 10: Auth & Freemium Gating

**Files:**
- Modify: `frontend/app/layout.tsx`
- Create: `frontend/middleware.ts`
- Modify: `frontend/app/athletes/[id]/page.tsx`

**Step 1: Install Clerk**

```bash
cd frontend && npm install @clerk/nextjs
```

**Step 2: Wrap app with ClerkProvider**

Modify `frontend/app/layout.tsx`:
```tsx
import { ClerkProvider } from "@clerk/nextjs";
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NILTrack — College Athlete NIL Valuations",
  description: "Predicted NIL valuations for college athletes, updated weekly.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body>{children}</body>
      </html>
    </ClerkProvider>
  );
}
```

**Step 3: Gate score breakdown behind Pro**

In `frontend/app/athletes/[id]/page.tsx`, wrap the Score Breakdown section:
```tsx
import { auth } from "@clerk/nextjs/server";

// Inside the page component, after fetching athlete:
const { userId } = await auth();
const isPro = false; // TODO: check subscription status via Clerk metadata

// Replace the breakdown section:
{isPro ? (
  <BreakdownSection components={athlete.components} />
) : (
  <div className="bg-[#111111] rounded-xl border border-[#1f1f1f] p-6 text-center">
    <p className="text-[#8a8a8a] text-sm mb-3">Score breakdown available on Pro</p>
    <a href="/upgrade" className="bg-white text-black px-4 py-2 rounded-full text-sm font-semibold">
      Upgrade to Pro — $9.99/mo
    </a>
  </div>
)}
```

**Step 4: Commit**

```bash
git add frontend/
git commit -m "feat: Clerk auth + freemium gating for score breakdown"
```

---

### Task 11: Deploy

**Step 1: Deploy frontend to Vercel**

```bash
cd frontend
npx vercel --prod
```
Set environment variables in Vercel dashboard:
- `NEXT_PUBLIC_API_URL` → Railway backend URL
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- `CLERK_SECRET_KEY`

**Step 2: Deploy backend to Railway**

```bash
# Install Railway CLI
npm install -g @railway/cli
railway login
railway init
railway up
```
Set environment variables in Railway dashboard:
- `DATABASE_URL` → Neon connection string
- `REDIS_URL` → Railway Redis URL
- `ANTHROPIC_API_KEY`

**Step 3: Schedule weekly pipeline**

In Railway dashboard → add cron job:
- Command: `python -m backend.jobs.weekly_refresh`
- Schedule: `0 3 * * 1` (Monday 3am EST)

**Step 4: Final commit**

```bash
git add .
git commit -m "feat: production deployment config — Vercel + Railway + Neon"
```

---

## Summary

| Task | Component | Est. Complexity |
|---|---|---|
| 1 | Project scaffold | Low |
| 2 | Database schema | Low |
| 3 | Scoring engine | Medium |
| 4 | Scrapers | Medium |
| 5 | API endpoints | Medium |
| 6 | Frontend design system | Low |
| 7 | Home + leaderboard | Medium |
| 8 | Athlete detail | Medium |
| 9 | Weekly pipeline | Medium |
| 10 | Auth + freemium | Low |
| 11 | Deploy | Low |

**Total: ~11 focused tasks, each 30-90 minutes of focused work.**
