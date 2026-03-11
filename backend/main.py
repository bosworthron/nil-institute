import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="NIL Institute API")

from backend.api.athletes import router as athletes_router
from backend.api.leaderboard import router as leaderboard_router

app.include_router(athletes_router)
app.include_router(leaderboard_router)

origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/admin/run-pipeline")
async def run_pipeline(background_tasks: __import__("fastapi").BackgroundTasks):
    from backend.jobs.weekly_refresh import run
    background_tasks.add_task(run)
    return {"status": "started"}
