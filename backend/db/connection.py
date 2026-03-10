import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

_raw_url = os.getenv("DATABASE_URL", "")
DATABASE_URL = _raw_url.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(DATABASE_URL, echo=False) if DATABASE_URL else None
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False) if engine else None

async def get_db():
    if AsyncSessionLocal is None:
        raise RuntimeError("Database not configured — set DATABASE_URL in .env")
    async with AsyncSessionLocal() as session:
        yield session
