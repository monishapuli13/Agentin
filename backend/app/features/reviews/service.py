from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.features.agents.models import Agent, AgentActivity, AgentPortfolioItem
from app.features.auth.models import User
from app.features.bids.models import Bid
from app.features.common.enums import ActivityType, ProjectStatus, ReviewStatus
from app.features.projects.models import Project
from app.features.projects.service import get_user_project
from app.features.reviews.models import Review
from app.features.reviews.schemas import ReputationUpdate, ReviewCreate


def create_project_review(
    db: Session,
    project_id: UUID,
    request: ReviewCreate,
    current_user: User,
) -> tuple[Review, ReputationUpdate]:
    project = get_user_project(db, project_id, current_user)

    if project.status != ProjectStatus.REVIEW:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project must be in review before a client review can be created.",
        )
    if project.review is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project has already been reviewed.",
        )

    review = Review(
        project_id=project.id,
        client_id=current_user.id,
        agent_id=project.assigned_agent_id,
        rating=request.rating,
        quality_score=request.quality_score,
        timeliness_score=request.timeliness_score,
        comment=request.comment.strip() if request.comment else None,
        status=ReviewStatus.PUBLISHED,
    )
    db.add(review)

    project.status = ProjectStatus.COMPLETED
    project.completed_at = datetime.now(timezone.utc)
    execution_result = dict(project.execution_result or {})
    transitions = list(execution_result.get("status_transitions", []))
    if ProjectStatus.COMPLETED.value not in transitions:
        transitions.append(ProjectStatus.COMPLETED.value)
    execution_result["status_transitions"] = transitions
    project.execution_result = execution_result
    db.flush()

    _create_completion_profile_records(db, project, review)
    reputation = recalculate_agent_reputation(db, project.assigned_agent_id)

    db.commit()
    db.refresh(review)
    db.refresh(project.assigned_agent)
    return review, reputation


def recalculate_agent_reputation(db: Session, agent_id: UUID) -> ReputationUpdate:
    agent = db.get(Agent, agent_id)
    if agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found.")

    reviews = list(db.scalars(select(Review).where(Review.agent_id == agent_id)).all())
    jobs_completed = len(reviews)

    if jobs_completed == 0:
        agent.average_rating = Decimal("0.00")
        agent.reputation_score = Decimal("0.00")
        agent.success_rate = Decimal("0.00")
        agent.jobs_completed = 0
        agent.simulated_earnings_cents = 0
        db.flush()
        return _reputation_update(agent)

    average_rating = _decimal_average(review.rating for review in reviews)
    average_quality = _decimal_average(review.quality_score for review in reviews)
    average_timeliness = _decimal_average(review.timeliness_score for review in reviews)
    reputation_score = _quantize(
        (average_rating * Decimal("0.50"))
        + (average_quality * Decimal("0.30"))
        + (average_timeliness * Decimal("0.20"))
    )
    successful_reviews = sum(1 for review in reviews if review.rating >= 4)
    success_rate = _quantize(
        (Decimal(successful_reviews) / Decimal(jobs_completed)) * Decimal("100")
    )

    total_earnings = sum(
        db.scalars(
            select(Bid.amount_cents)
            .join(Project, Project.selected_bid_id == Bid.id)
            .join(Review, Review.project_id == Project.id)
            .where(Review.agent_id == agent_id)
        ).all()
    )

    agent.average_rating = average_rating
    agent.reputation_score = reputation_score
    agent.jobs_completed = jobs_completed
    agent.success_rate = success_rate
    agent.simulated_earnings_cents = int(total_earnings)

    db.add(
        AgentActivity(
            agent_id=agent.id,
            activity_type=ActivityType.REPUTATION_UPDATED.value,
            title="Reputation updated",
            description=(
                f"{agent.name}'s reputation is now {reputation_score} after "
                f"{jobs_completed} completed project{'s' if jobs_completed != 1 else ''}."
            ),
            activity_metadata={
                "average_rating": str(average_rating),
                "reputation_score": str(reputation_score),
                "success_rate": str(success_rate),
                "jobs_completed": jobs_completed,
            },
        )
    )
    db.flush()
    return _reputation_update(agent)


def _create_completion_profile_records(db: Session, project: Project, review: Review) -> None:
    job = project.job
    agent = project.assigned_agent
    deliverable_summary = (project.execution_result or {}).get("deliverable_summary")

    db.add(
        AgentPortfolioItem(
            agent_id=agent.id,
            title=job.title,
            description=deliverable_summary or f"Completed project: {job.title}.",
            skills=job.required_skills,
            result_summary=review.comment or deliverable_summary,
        )
    )
    db.add(
        AgentActivity(
            agent_id=agent.id,
            activity_type=ActivityType.PROJECT_COMPLETED.value,
            title="Project completed",
            description=f"{agent.name} completed '{job.title}' and received {review.rating}/5.",
            activity_metadata={
                "project_id": str(project.id),
                "job_id": str(job.id),
                "rating": review.rating,
                "quality_score": review.quality_score,
                "timeliness_score": review.timeliness_score,
            },
        )
    )
    db.add(
        AgentActivity(
            agent_id=agent.id,
            activity_type=ActivityType.REVIEW_RECEIVED.value,
            title="Review received",
            description=review.comment or f"Received a {review.rating}/5 client review.",
            activity_metadata={
                "project_id": str(project.id),
                "review_id": str(review.id),
                "rating": review.rating,
            },
        )
    )


def _decimal_average(values) -> Decimal:
    values = list(values)
    return _quantize(Decimal(sum(values)) / Decimal(len(values)))


def _quantize(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _reputation_update(agent: Agent) -> ReputationUpdate:
    return ReputationUpdate(
        agent_id=agent.id,
        reputation_score=agent.reputation_score,
        average_rating=agent.average_rating,
        jobs_completed=agent.jobs_completed,
        success_rate=agent.success_rate,
        simulated_earnings_cents=agent.simulated_earnings_cents,
    )
