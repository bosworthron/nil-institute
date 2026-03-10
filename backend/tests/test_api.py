import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_leaderboard_returns_athletes_key():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/leaderboard?sport=football&limit=10")
    assert resp.status_code == 200
    assert "athletes" in resp.json()

@pytest.mark.asyncio
async def test_leaderboard_default_sport():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/leaderboard")
    assert resp.status_code == 200

@pytest.mark.asyncio
async def test_athlete_not_found_returns_404():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/athletes/nonexistent-athlete-id")
    assert resp.status_code == 404

@pytest.mark.asyncio
async def test_search_returns_athletes_key():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/athletes?q=test")
    assert resp.status_code == 200
    assert "athletes" in resp.json()

@pytest.mark.asyncio
async def test_leaderboard_limit_param():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/leaderboard?limit=5")
    assert resp.status_code == 200
