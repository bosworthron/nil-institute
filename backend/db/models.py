from sqlalchemy import Column, String, Float, Integer, Date, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
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
