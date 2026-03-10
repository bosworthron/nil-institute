# NIL Stock Market — Design Document
**Date:** 2026-03-10
**Status:** Approved

---

## Overview

A public-facing web app where every college football and men's basketball player has a NIL valuation displayed like a stock ticker — with a score, trend direction, and % change. Fans browse, search, filter, and track athletes the same way they'd browse stocks on Robinhood.

Target audience: fans, media, agents, brands, collectives — anyone who wants to see predicted NIL value for a player.

---

## Core Product

### The NIL Score

A single composite dollar value (e.g. $847K) derived from four weighted inputs, refreshed weekly:

| Input | Weight | Source |
|---|---|---|
| Social following + engagement rate | 35% | Scraped (Instagram, X/Twitter, TikTok) |
| Athletic performance / recruiting rank | 30% | Scraped (ESPN, 247Sports, On3) |
| School market size + program prestige | 20% | Public data (enrollment, media market, AP rankings) |
| Sport + position demand | 15% | AI-estimated from deal trend data |

Score changes display as +/- % with green/red indicators, exactly like a stock price.

### Core Pages

- **Home** — trending athletes, biggest movers this week, sport/conference filters
- **Athlete Page** — score history chart, composite breakdown, comparable athletes
- **Leaderboard** — top 100 filterable by sport, conference, school, position
- **Search** — find any athlete instantly

---

## Architecture

### Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| Frontend | Next.js + Tailwind | SEO-friendly, fast, great for public data pages |
| Backend | Python (FastAPI) | Best for scraping pipelines + AI inference |
| Database | Neon (Postgres) | Serverless, auto-scales, branching for dev/prod |
| Cache | Redis on Railway | Hot cache for leaderboards and athlete pages |
| AI Layer | Claude API | Composite score inference, news summarization, gap filling |
| Scraping | Playwright + BeautifulSoup | Handles JS-rendered sports sites |
| Frontend Hosting | Vercel | Fast deploys, CDN, zero ops |
| Backend Hosting | Railway | Simple managed hosting for FastAPI + Redis |
| Auth | Clerk | Freemium gating with minimal setup |

### Data Pipeline (Weekly — runs Monday 3am EST)

```
Scrapers fire in parallel:
  - ESPN/247Sports → athletic stats, recruiting ranks
  - On3 → existing NIL valuations (reference signal)
  - Instagram/X/TikTok → follower counts, engagement rates
        ↓
Raw data stored in Neon (raw_athlete_data table)
        ↓
Claude API normalizes + fills inference gaps
        ↓
Scoring engine calculates composite NIL score
        ↓
Delta computed vs prior week → stored in score_history
        ↓
Redis cache refreshed → frontend serves instantly
```

### Real-Time Layer

Breaking news events (transfer portal, injury, viral moment) trigger manual re-score via admin dashboard outside the weekly cycle.

---

## Sports Coverage

- **Launch:** College Football (FBS, ~4,500 players) + Men's Basketball
- **Expansion:** All Power 4 sports → all college sports including women's (fastest growing NIL segment)

Launch timing targets **August 2026** to align with college football season hype.

---

## Monetization

### Freemium Tiers

| Feature | Free | Pro ($9.99/mo) |
|---|---|---|
| Current NIL score | ✅ | ✅ |
| Leaderboards + search | ✅ | ✅ |
| Score history (last 4 weeks) | ✅ | ✅ |
| Full score history + trend chart | ❌ | ✅ |
| Composite score breakdown | ❌ | ✅ |
| Price alerts (score moves 10%+) | ❌ | ✅ |
| Similar athletes comparisons | ❌ | ✅ |
| CSV data export | ❌ | ✅ |

### Advertising

- Sponsor slots on leaderboards and athlete pages (brands already active in NIL: energy drinks, fintech, apparel)
- "Presented by" placement on weekly Top Movers digest email
- Conference/school sponsorships (e.g. "SEC Leaderboard presented by [Brand]")

### Conservative Year 1 Revenue Target

| Source | Target | Monthly |
|---|---|---|
| Pro subscribers | 1,000 users | $9,990 |
| Ad revenue | 500K pageviews/mo | ~$2,500 |
| **Total** | | **~$12,500/mo** |

---

## Growth Loop

```
Fan searches player → sees score → shares it →
friend visits → sees leaderboard → follows athletes →
score moves → gets hooked → upgrades to Pro
```

---

## Launch Plan (12 Weeks)

| Phase | Weeks | Goal |
|---|---|---|
| Foundation | 1–3 | Data pipeline + scoring engine + DB schema |
| MVP UI | 4–6 | Home, leaderboard, athlete page, search |
| Polish | 7–9 | Robinhood UI feel, mobile-responsive, auth + Pro tier |
| Launch | 10–12 | SEO, Reddit/Twitter fan communities, ad setup |

---

## Agent Tooling (agency-agents)

The `msitarzewski/agency-agents` repo provides specialized Claude Code agent personalities used across the build:

| Agent | Role |
|---|---|
| Backend Architect | FastAPI design, Neon schema |
| AI Engineer | Claude scoring pipeline |
| Frontend Developer | Next.js Robinhood-style UI |
| Data Engineer | Scraping pipeline |
| Growth Hacker | Fan acquisition strategy |
| Legal Compliance Checker | NCAA/NIL regulatory review |
| Security Engineer | Scraping ethics, data handling |
