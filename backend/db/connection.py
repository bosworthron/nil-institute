import os
import re
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

_raw_url = os.getenv("DATABASE_URL", "")

def _build_async_url(raw: str) -> str:
    """
    Convert a standard postgresql:// URL to postgresql+asyncpg://.
    asyncpg does not accept sslmode= or channel_binding= query params —
    strip them out and pass ssl via connect_args instead.
    """
    url = raw.replace("postgresql://", "postgresql+asyncpg://")
    url = re.sub(r"[?&]sslmode=[^&]*", "", url)
    url = re.sub(r"[?&]channel_binding=[^&]*", "", url)
    # Clean up trailing ? or & left after stripping
    url = re.sub(r"[?&]$", "", url)
    return url

DATABASE_URL = _build_async_url(_raw_url) if _raw_url else ""

# asyncpg needs ssl=True when connecting to Neon (replaces sslmode=require)
_connect_args = {"ssl": True} if _raw_url else {}

engine = create_async_engine(DATABASE_URL, echo=False, connect_args=_connect_args) if DATABASE_URL else None
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False) if engine else None

async def get_db():
    if AsyncSessionLocal is None:
        raise RuntimeError("Database not configured — set DATABASE_URL in .env")
    async with AsyncSessionLocal() as session:
        yield session
