from decimal import Decimal
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session, selectinload

from app.features.agents.models import Agent, AgentActivity
from app.features.agents.seed import seed_agents
from app.features.ai.service import generate_bid_with_ai
from app.features.auth.models import User
from app.features.bids.models import Bid
from app.features.common.enums import ActivityType, BidStatus, JobStatus, ProjectStatus
from app.features.jobs.models import Job
from app.features.jobs.schemas import JobCreate
from app.features.projects.models import Project
from app.features.projects.service import generate_project_execution_plan


def create_job_with_bids(db: Session, request: JobCreate, current_user: User) -> tuple[Job, list[Bid]]:
    job = Job(
        client_id=current_user.id,
        title=request.title.strip(),
        description=request.description.strip(),
        budget_cents=request.budget_cents,
        category=request.category.strip() if request.category else None,
        required_skills=_normalize_skills(request.required_skills),
        deadline_at=request.deadline_at,
        status=JobStatus.BIDDING,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    bids = generate_bids_for_job(db, job)
    db.refresh(job)
    return job, bids


def list_jobs(
    db: Session,
    status_filter: JobStatus | None = None,
    category: str | None = None,
    skill: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Job]:
    query = select(Job)
    if status_filter:
        query = query.where(Job.status == status_filter)
    if category:
        query = query.where(Job.category == category)

    jobs = list(db.scalars(query.order_by(desc(Job.created_at)).offset(offset).limit(limit)).all())

    if skill:
        normalized_skill = skill.strip().lower()
        jobs = [
            job
            for job in jobs
            if normalized_skill in {item.lower() for item in job.required_skills}
        ]

    return jobs


def get_job_or_404(db: Session, job_id: UUID) -> Job:
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    return job


def list_job_bids(db: Session, job_id: UUID, current_user: User) -> list[Bid]:
    job = get_job_or_404(db, job_id)
    _ensure_job_owner(job, current_user)

    return list(
        db.scalars(
            select(Bid)
            .where(Bid.job_id == job_id)
            .options(selectinload(Bid.agent))
            .order_by(desc(Bid.confidence_score), Bid.amount_cents)
        ).all()
    )


def select_winning_bid(db: Session, job_id: UUID, bid_id: UUID, current_user: User) -> tuple[Job, Bid, Project]:
    job = get_job_or_404(db, job_id)
    _ensure_job_owner(job, current_user)

    if job.status not in {JobStatus.BIDDING, JobStatus.OPEN}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A winning bid can only be selected while the job is in bidding.",
        )

    winning_bid = db.scalar(
        select(Bid)
        .where(Bid.id == bid_id, Bid.job_id == job_id)
        .options(selectinload(Bid.agent))
    )
    if not winning_bid:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bid not found.")

    for bid in db.scalars(select(Bid).where(Bid.job_id == job_id)).all():
        bid.status = BidStatus.SELECTED if bid.id == winning_bid.id else BidStatus.REJECTED

    job.status = JobStatus.AWARDED
    project = Project(
        job_id=job.id,
        selected_bid_id=winning_bid.id,
        assigned_agent_id=winning_bid.agent_id,
        status=ProjectStatus.ASSIGNED,
    )
    db.add(project)
    db.flush()
    generate_project_execution_plan(db, project)
    db.add(
        AgentActivity(
            agent_id=winning_bid.agent_id,
            activity_type=ActivityType.BID_SELECTED.value,
            title="Bid selected",
            description=f"{winning_bid.agent.name} was selected for '{job.title}'.",
            activity_metadata={
                "job_id": str(job.id),
                "bid_id": str(winning_bid.id),
                "project_id": str(project.id),
            },
        )
    )
    db.commit()
    db.refresh(job)
    db.refresh(winning_bid)
    db.refresh(project)
    return job, winning_bid, project


def generate_bids_for_job(db: Session, job: Job) -> list[Bid]:
    _ensure_mvp_agents(db)
    agents = list(db.scalars(select(Agent).where(Agent.is_active.is_(True))).all())
    ranked_agents = sorted(
        agents,
        key=lambda agent: (
            _calculate_skill_match(agent.skills, job.required_skills)["score"],
            Decimal(str(agent.reputation_score)),
        ),
        reverse=True,
    )[:3]

    bids: list[Bid] = []
    for agent in ranked_agents:
        skill_match = _calculate_skill_match(agent.skills, job.required_skills)
        generated_bid = generate_bid_with_ai(agent, job, skill_match)
        bid = Bid(
            job_id=job.id,
            agent_id=agent.id,
            amount_cents=generated_bid.amount_cents,
            estimated_hours=Decimal(str(generated_bid.estimated_hours)),
            proposal=generated_bid.proposal,
            confidence_score=Decimal(str(generated_bid.confidence_score)),
            reasoning=generated_bid.reasoning,
            skill_match=skill_match,
            status=BidStatus.PENDING,
        )
        db.add(bid)
        db.add(
            AgentActivity(
                agent_id=agent.id,
                activity_type=ActivityType.BID_CREATED.value,
                title="Bid created",
                description=f"{agent.name} placed a bid on '{job.title}'.",
                activity_metadata={
                    "job_id": str(job.id),
                    "amount_cents": generated_bid.amount_cents,
                    "confidence_score": generated_bid.confidence_score,
                },
            )
        )
        bids.append(bid)

    db.commit()
    for bid in bids:
        db.refresh(bid)

    return bids


def _ensure_job_owner(job: Job, current_user: User) -> None:
    if job.client_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this job.",
        )


def _ensure_mvp_agents(db: Session) -> None:
    agent_count = db.scalar(select(func.count()).select_from(Agent).where(Agent.is_active.is_(True)))
    if (agent_count or 0) < 3:
        seed_agents(db)


def _normalize_skills(skills: list[str]) -> list[str]:
    normalized = []
    seen = set()
    for skill in skills:
        item = skill.strip().lower()
        if item and item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _calculate_skill_match(agent_skills: dict[str, float], required_skills: list[str]) -> dict[str, Any]:
    normalized_agent_skills = {key.lower(): value for key, value in agent_skills.items()}
    normalized_required = _normalize_skills(required_skills)

    if not normalized_required:
        return {
            "score": 0.7,
            "matched_skills": [],
            "missing_skills": [],
        }

    matched_skills = [
        skill for skill in normalized_required if skill in normalized_agent_skills
    ]
    missing_skills = [
        skill for skill in normalized_required if skill not in normalized_agent_skills
    ]
    proficiency = sum(float(normalized_agent_skills[skill]) for skill in matched_skills)
    score = proficiency / len(normalized_required)

    return {
        "score": round(score, 4),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
    }
