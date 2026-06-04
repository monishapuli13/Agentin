import uuid

from fastapi import HTTPException, status
from sqlalchemy import desc, or_, select
from sqlalchemy.orm import Session, selectinload

from app.features.agents.models import Agent
from app.features.agents.schemas import (
    AgentDetail,
    AgentReputationSummary,
    AgentSummary,
    AgentWorkHistoryItem,
)
from app.features.bids.models import Bid
from app.features.common.enums import ProjectStatus
from app.features.jobs.models import Job
from app.features.projects.models import Project
from app.features.reviews.models import Review


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


def get_agent_detail(db: Session, agent_id_or_slug: str) -> AgentDetail:
    agent = get_agent_by_id_or_slug(db, agent_id_or_slug)
    summary = AgentSummary.model_validate(agent).model_dump()
    work_history = _agent_work_history(db, agent)

    return AgentDetail(
        **summary,
        bio=agent.bio,
        personality=agent.personality,
        average_response_seconds=agent.average_response_seconds,
        portfolio_items=agent.portfolio_items,
        activities=sorted(agent.activities, key=lambda item: item.created_at, reverse=True),
        work_history=work_history,
        completed_projects=agent.jobs_completed,
        earnings_cents=agent.simulated_earnings_cents,
        reputation_summary=AgentReputationSummary(
            reputation_score=agent.reputation_score,
            average_rating=agent.average_rating,
            jobs_completed=agent.jobs_completed,
            success_rate=agent.success_rate,
            simulated_earnings_cents=agent.simulated_earnings_cents,
        ),
    )


def _agent_work_history(db: Session, agent: Agent) -> list[AgentWorkHistoryItem]:
    rows = db.execute(
        select(Project, Job, Bid, Review)
        .join(Job, Project.job_id == Job.id)
        .join(Bid, Project.selected_bid_id == Bid.id)
        .join(Review, Review.project_id == Project.id)
        .where(
            Project.assigned_agent_id == agent.id,
            Project.status == ProjectStatus.COMPLETED,
        )
        .order_by(desc(Project.completed_at))
    ).all()

    return [
        AgentWorkHistoryItem(
            project_id=project.id,
            job_id=job.id,
            job_title=job.title,
            rating=review.rating,
            quality_score=review.quality_score,
            timeliness_score=review.timeliness_score,
            comment=review.comment,
            amount_cents=bid.amount_cents,
            completed_at=project.completed_at,
        )
        for project, job, bid, review in rows
    ]
