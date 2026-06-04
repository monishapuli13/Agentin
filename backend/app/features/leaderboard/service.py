from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.features.agents.models import Agent
from app.features.leaderboard.schemas import LeaderboardEntry


def top_rated_agents(db: Session, limit: int = 10) -> list[LeaderboardEntry]:
    return _ranked_agents(
        db,
        order_by=[
            desc(Agent.average_rating),
            desc(Agent.reputation_score),
            desc(Agent.jobs_completed),
        ],
        limit=limit,
    )


def most_completed_agents(db: Session, limit: int = 10) -> list[LeaderboardEntry]:
    return _ranked_agents(
        db,
        order_by=[
            desc(Agent.jobs_completed),
            desc(Agent.average_rating),
            desc(Agent.reputation_score),
        ],
        limit=limit,
    )


def highest_earning_agents(db: Session, limit: int = 10) -> list[LeaderboardEntry]:
    return _ranked_agents(
        db,
        order_by=[
            desc(Agent.simulated_earnings_cents),
            desc(Agent.average_rating),
        ],
        limit=limit,
    )


def best_success_rate_agents(db: Session, limit: int = 10) -> list[LeaderboardEntry]:
    return _ranked_agents(
        db,
        order_by=[
            desc(Agent.success_rate),
            desc(Agent.jobs_completed),
            desc(Agent.average_rating),
        ],
        limit=limit,
    )


def _ranked_agents(db: Session, order_by, limit: int) -> list[LeaderboardEntry]:
    agents = list(
        db.scalars(
            select(Agent)
            .where(Agent.is_active.is_(True))
            .order_by(*order_by)
            .limit(limit)
        ).all()
    )
    return [
        LeaderboardEntry(
            rank=index,
            agent_id=agent.id,
            slug=agent.slug,
            name=agent.name,
            headline=agent.headline,
            specialization=agent.specialization,
            reputation_score=agent.reputation_score,
            average_rating=agent.average_rating,
            jobs_completed=agent.jobs_completed,
            success_rate=agent.success_rate,
            simulated_earnings_cents=agent.simulated_earnings_cents,
        )
        for index, agent in enumerate(agents, start=1)
    ]

