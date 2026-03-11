"""
ESPN API scraper — pulls live college rosters for NIL scoring.
Replaces hardcoded SEED_ATHLETES with real active roster data.
"""
import asyncio
import httpx

ESPN_SITE = "https://site.api.espn.com/apis/site/v2/sports"

# Power schools — bump follower estimates to "top" tier
POWER_SCHOOLS = {
    # Football
    "Alabama", "Ohio State", "Georgia", "Michigan", "Texas", "LSU",
    "Notre Dame", "Clemson", "Penn State", "Oregon", "Florida State",
    "Oklahoma", "USC", "Tennessee", "Colorado", "Nebraska", "Auburn",
    # Basketball
    "Duke", "Kentucky", "Kansas", "UConn", "Gonzaga", "North Carolina",
    "Indiana", "Baylor", "Houston", "Iowa", "South Carolina", "UCLA",
    "Arizona", "Villanova", "Louisville", "Marquette",
}

# Follower estimates by (sport, position_abbr, tier)
FOLLOWER_TIERS = {
    ("football",         "QB",      "top"): (800_000, 300_000, 4.0),
    ("football",         "QB",      "mid"): (120_000,  45_000, 2.8),
    ("football",         "WR",      "top"): (350_000, 130_000, 3.5),
    ("football",         "WR",      "mid"):  (80_000,  30_000, 2.5),
    ("football",         "RB",      "top"): (250_000,  90_000, 3.2),
    ("football",         "RB",      "mid"):  (60_000,  22_000, 2.3),
    ("football",         "EDGE",    "top"): (150_000,  55_000, 2.9),
    ("football",         "EDGE",    "mid"):  (45_000,  17_000, 2.2),
    ("football",         "CB",      "top"): (130_000,  48_000, 2.7),
    ("football",         "CB",      "mid"):  (40_000,  15_000, 2.1),
    ("football",         "default", "top"):  (90_000,  34_000, 2.6),
    ("football",         "default", "mid"):  (35_000,  13_000, 2.1),
    ("mens_basketball",  "G",       "top"): (400_000, 150_000, 4.0),
    ("mens_basketball",  "G",       "mid"):  (70_000,  26_000, 2.6),
    ("mens_basketball",  "F",       "top"): (300_000, 110_000, 3.5),
    ("mens_basketball",  "F",       "mid"):  (55_000,  20_000, 2.4),
    ("mens_basketball",  "C",       "top"): (200_000,  75_000, 3.0),
    ("mens_basketball",  "C",       "mid"):  (40_000,  15_000, 2.2),
    ("mens_basketball",  "default", "top"): (150_000,  55_000, 3.0),
    ("mens_basketball",  "default", "mid"):  (40_000,  15_000, 2.2),
    ("womens_basketball","G",       "top"): (600_000, 200_000, 5.0),
    ("womens_basketball","G",       "mid"):  (80_000,  28_000, 3.0),
    ("womens_basketball","F",       "top"): (400_000, 140_000, 4.5),
    ("womens_basketball","F",       "mid"):  (65_000,  22_000, 2.8),
    ("womens_basketball","C",       "top"): (180_000,  62_000, 3.2),
    ("womens_basketball","C",       "mid"):  (45_000,  16_000, 2.3),
    ("womens_basketball","default", "top"): (200_000,  70_000, 3.5),
    ("womens_basketball","default", "mid"):  (50_000,  18_000, 2.5),
}


def _follower_estimate(sport: str, position_abbr: str, school: str) -> tuple[int, int, float]:
    tier = "top" if school in POWER_SCHOOLS else "mid"
    pos = (position_abbr or "").upper()
    key = (sport, pos, tier)
    if key not in FOLLOWER_TIERS:
        key = (sport, "default", tier)
    return FOLLOWER_TIERS[key]


def _year_from_experience(exp: dict | None) -> str:
    years = (exp or {}).get("years", 0)
    return {0: "Freshman", 1: "Sophomore", 2: "Junior", 3: "Senior"}.get(years, "Senior")


async def _fetch(client: httpx.AsyncClient, url: str) -> dict:
    resp = await client.get(url, timeout=15)
    resp.raise_for_status()
    return resp.json()


async def _fetch_teams(client: httpx.AsyncClient, sport_path: str) -> list[dict]:
    url = f"{ESPN_SITE}/{sport_path}/teams?limit=500"
    data = await _fetch(client, url)
    teams = data.get("sports", [{}])[0].get("leagues", [{}])[0].get("teams", [])
    return [t["team"] for t in teams if t.get("team")]


async def _fetch_roster(client: httpx.AsyncClient, sport_path: str, team_id: str) -> list[dict]:
    url = f"{ESPN_SITE}/{sport_path}/teams/{team_id}/roster"
    try:
        data = await _fetch(client, url)
    except Exception:
        return []

    athletes = data.get("athletes", [])
    team_info = data.get("team", {})

    # Football returns grouped (items); basketball returns flat list
    flat = []
    if athletes and "items" in (athletes[0] if athletes else {}):
        for group in athletes:
            for a in group.get("items", []):
                a["_team"] = team_info
                flat.append(a)
    else:
        for a in athletes:
            a["_team"] = team_info
            flat.append(a)
    return flat


def _map_athlete(raw: dict, sport: str) -> dict | None:
    name = (raw.get("fullName") or "").strip()
    if not name:
        return None
    if (raw.get("status") or {}).get("type", "active") != "active":
        return None

    team = raw.get("_team", {})
    school = team.get("location") or team.get("displayName", "Unknown")
    conference = (team.get("conference") or {}).get("name", "")
    position_abbr = (raw.get("position") or {}).get("abbreviation", "")
    year = _year_from_experience(raw.get("experience"))
    ig, tw, er = _follower_estimate(sport, position_abbr, school)

    return {
        "name": name,
        "school": school,
        "sport": sport,
        "position": position_abbr,
        "year": year,
        "conference": conference,
        "instagram_followers": ig,
        "twitter_followers": tw,
        "engagement_rate": er,
        "recruiting_rank": None,
    }


async def scrape_college_athletes(
    max_football: int = 150,
    max_mens_bb: int = 100,
    max_womens_bb: int = 75,
) -> list[dict]:
    """Pull live rosters from ESPN. Returns athletes ready for NIL scoring."""
    results: list[dict] = []

    async with httpx.AsyncClient() as client:
        for sport, sport_path, max_count in [
            ("football",          "football/college-football",               max_football),
            ("mens_basketball",   "basketball/mens-college-basketball",      max_mens_bb),
            ("womens_basketball", "basketball/womens-college-basketball",    max_womens_bb),
        ]:
            gender = sport_path.split("/")[1].split("-")[0] if "basketball" in sport_path else None
            print(f"Fetching {sport} rosters...", flush=True)

            teams = await _fetch_teams(client, sport_path)
            # Prioritize power schools
            teams.sort(key=lambda t: (0 if t.get("location", "") in POWER_SCHOOLS else 1))

            athletes: list[dict] = []
            for team in teams:
                if len(athletes) >= max_count:
                    break
                roster = await _fetch_roster(client, sport_path, team["id"])
                for raw in roster:
                    if len(athletes) >= max_count:
                        break
                    mapped = _map_athlete(raw, sport)
                    if mapped:
                        athletes.append(mapped)

            print(f"  → {len(athletes)} {sport} athletes", flush=True)
            results.extend(athletes)

    return results


if __name__ == "__main__":
    async def main():
        athletes = await scrape_college_athletes()
        print(f"\nTotal: {len(athletes)} athletes")
        for a in athletes[:5]:
            print(f"  {a['name']} | {a['school']} | {a['sport']} | {a['position']}")

    asyncio.run(main())
