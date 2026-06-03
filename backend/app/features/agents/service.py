import uuid

from fastapi import HTTPException, status
from sqlalchemy import desc, or_, select
from sqlalchemy.orm import Session, selectinload

from app.features.agents.models import Agent


def list_agents(
    db: Session,
    specialization: str | None = None,
    skill: str | None = None,
    min_reputation: float = 0,
    sort: str = "reputation",
    limit: int = 20,
    offset: int = 0,
) -> list[Agent]:
    query = select(Agent).where(Agent.is_active.is_(True))

    if specialization:
        query = query.where(Agent.specialization == specialization)
    if min_reputation:
        query = query.where(Agent.reputation_score >= min_reputation)

    if sort == "earnings":
        query = query.order_by(desc(Agent.simulated_earnings_cents))
    elif sort == "completed":
        query = query.order_by(desc(Agent.jobs_completed))
    else:
        query = query.order_by(desc(Agent.reputation_score))

    agents = list(db.scalars(query.offset(offset).limit(limit)).all())

    if skill:
        normalized_skill = skill.strip().lower()
        agents = [
            agent
            for agent in agents
            if normalized_skill in {item.lower() for item in agent.skills.keys()}
        ]

    return agents


def get_agent_by_id_or_slug(db: Session, agent_id_or_slug: str) -> Agent:
    conditions = [Agent.slug == agent_id_or_slug]
    try:
        conditions.append(Agent.id == uuid.UUID(agent_id_or_slug))
    except ValueError:
        pass

    agent = db.scalar(
        select(Agent)
        .where(or_(*conditions), Agent.is_active.is_(True))
        .options(
            selectinload(Agent.portfolio_items),
            selectinload(Agent.activities),
        )
    )
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found.",
        )

    return agent

