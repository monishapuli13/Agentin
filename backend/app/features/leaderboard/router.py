from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.schemas import ApiResponse, api_response
from app.features.leaderboard.schemas import LeaderboardEntry
from app.features.leaderboard.service import (
    best_success_rate_agents,
    highest_earning_agents,
    most_completed_agents,
    top_rated_agents,
)

router = APIRouter()


@router.get("/top-rated", response_model=ApiResponse[list[LeaderboardEntry]])
def top_rated(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return api_response(top_rated_agents(db, limit=limit))


@router.get("/most-completed", response_model=ApiResponse[list[LeaderboardEntry]])
def most_completed(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return api_response(most_completed_agents(db, limit=limit))


@router.get("/highest-earnings", response_model=ApiResponse[list[LeaderboardEntry]])
def highest_earnings(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return api_response(highest_earning_agents(db, limit=limit))


@router.get("/best-success-rate", response_model=ApiResponse[list[LeaderboardEntry]])
def best_success_rate(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return api_response(best_success_rate_agents(db, limit=limit))

