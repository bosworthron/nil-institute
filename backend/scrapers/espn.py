import httpx
from bs4 import BeautifulSoup
from typing import List

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
}

# ESPN school ID mapping for major programs
SCHOOL_IDS = {
    "alabama": "333",
    "ohio-state": "194",
    "texas": "251",
    "georgia": "61",
    "michigan": "130",
    "colorado": "38",
    "duke": "150",
    "kansas": "2305",
}

async def scrape_espn_roster(school_slug: str, sport: str = "football") -> List[dict]:
    """
    Scrape basic roster data from ESPN.
    Returns list of raw athlete dicts (name, position, year, school, sport).
    Falls back to empty list on any error.
    """
    school_id = SCHOOL_IDS.get(school_slug)
    if not school_id:
        return []

    sport_path = "football" if sport == "football" else "mens-college-basketball"
    url = f"https://www.espn.com/college-{sport_path}/team/roster/_/id/{school_id}"

    try:
        async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=15) as client:
            resp = await client.get(url)
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        athletes = []

        rows = soup.select("table.Table tr.Table__TR")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 3:
                continue
            name_cell = cells[1].get_text(strip=True) if len(cells) > 1 else ""
            if not name_cell or name_cell.lower() in ("name", ""):
                continue
            athletes.append({
                "name": name_cell,
                "position": cells[2].get_text(strip=True) if len(cells) > 2 else "",
                "year": cells[4].get_text(strip=True) if len(cells) > 4 else "",
                "school": school_slug,
                "sport": sport,
            })

        return athletes

    except Exception:
        return []
