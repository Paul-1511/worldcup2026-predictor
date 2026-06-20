from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.services.data_loader import loader
from app.services.predictor import engine
from app.services.standings import compute_standings

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok", "models_ready": engine.ready}


@router.post("/refresh")
async def refresh_data():
    await loader.fetch_worldcup(force=True)
    return {"status": "refreshed", "last_fetch": loader.last_fetch}


@router.get("/matches")
async def get_matches(
    status: str | None = Query(None, description="scheduled|finished|all"),
):
    matches = loader.get_matches()
    if status and status != "all":
        matches = [m for m in matches if m["status"] == status]
    return {"count": len(matches), "matches": matches}


@router.get("/matches/{match_id}")
async def get_match(match_id: int):
    matches = loader.get_matches()
    if match_id < 0 or match_id >= len(matches):
        raise HTTPException(404, "Match not found")
    return matches[match_id]


@router.get("/scoreboard")
async def scoreboard():
    await loader.fetch_worldcup()
    matches = loader.get_matches()
    finished = sorted(
        [m for m in matches if m["status"] == "finished"],
        key=lambda x: (x["date"], x.get("time", "")),
        reverse=True,
    )[:15]
    live = [m for m in matches if m["status"] == "scheduled" and m.get("home_score") is not None]
    upcoming = sorted(
        [m for m in matches if m["status"] == "scheduled"],
        key=lambda x: (x["date"], x.get("time", "")),
    )[:10]
    standings = compute_standings(matches)
    return {
        "tournament": "FIFA World Cup 2026",
        "last_updated": loader.last_fetch,
        "recent_results": finished,
        "live": live,
        "upcoming": upcoming,
        "standings": standings,
        "stats": {
            "total_matches": len(matches),
            "finished": sum(1 for m in matches if m["status"] == "finished"),
            "remaining": sum(1 for m in matches if m["status"] == "scheduled"),
        },
    }


@router.get("/standings")
async def standings():
    matches = loader.get_matches()
    return compute_standings(matches)


@router.get("/predict/{home_team}/{away_team}")
async def predict_match(
    home_team: str,
    away_team: str,
    model: str = Query("both", pattern="^(poisson|xgboost|both)$"),
):
    return engine.predict_match(home_team, away_team, model=model)


@router.get("/predictions/upcoming")
async def predict_upcoming(
    model: str = Query("both", pattern="^(poisson|xgboost|both)$"),
    limit: int = Query(20, ge=1, le=50),
):
    preds = engine.predict_upcoming(model=model)
    return {"count": min(limit, len(preds)), "predictions": preds[:limit]}


@router.get("/teams")
async def teams():
    return sorted(loader.get_teams())
