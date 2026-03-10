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
