from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session, selectinload

from app.features.agents.models import AgentActivity
from app.features.ai.service import generate_execution_plan_with_ai
from app.features.auth.models import User
from app.features.common.enums import ActivityType, ProjectStatus, ProjectStepStatus
from app.features.jobs.models import Job
from app.features.projects.models import Project, ProjectStep


def generate_project_execution_plan(db: Session, project: Project) -> Project:
    transitions = [ProjectStatus.ASSIGNED.value]

    project.status = ProjectStatus.IN_PROGRESS
    project.started_at = datetime.now(timezone.utc)
    db.flush()
    transitions.append(ProjectStatus.IN_PROGRESS.value)

    generated_plan = generate_execution_plan_with_ai(
        project.assigned_agent,
        project.job,
        project.selected_bid,
    )

    plan_payload = generated_plan.model_dump()
    project.execution_plan = {
        "execution_plan": generated_plan.execution_plan,
        "milestones": generated_plan.milestones,
        "steps": [step.model_dump() for step in generated_plan.steps],
    }
    project.execution_result = {
        "deliverable_summary": generated_plan.deliverable_summary,
        "status_transitions": transitions + [ProjectStatus.REVIEW.value],
    }

    now = datetime.now(timezone.utc)
    for index, step in enumerate(generated_plan.steps, start=1):
        db.add(
            ProjectStep(
                project_id=project.id,
                step_index=index,
                title=step.title,
                description=step.description,
                status=ProjectStepStatus.COMPLETED,
                output=step.output,
                started_at=project.started_at,
                completed_at=now,
            )
        )

    project.status = ProjectStatus.REVIEW
    db.add(
        AgentActivity(
            agent_id=project.assigned_agent_id,
            activity_type=ActivityType.PROJECT_PLANNED.value,
            title="Execution plan generated",
            description=(
                f"{project.assigned_agent.name} generated a structured execution "
                f"plan for '{project.job.title}'."
            ),
            activity_metadata={
                "project_id": str(project.id),
                "job_id": str(project.job_id),
                "milestones": plan_payload["milestones"],
            },
        )
    )
    db.flush()
    return project


def list_user_projects(db: Session, current_user: User) -> list[Project]:
    return list(
        db.scalars(
            _project_query()
            .join(Job, Project.job_id == Job.id)
            .where(Job.client_id == current_user.id)
            .order_by(desc(Project.created_at))
        ).all()
    )


def get_user_project(db: Session, project_id: UUID, current_user: User) -> Project:
    project = db.scalar(
        _project_query()
        .join(Job, Project.job_id == Job.id)
        .where(Project.id == project_id, Job.client_id == current_user.id)
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )
    return project


def get_project_execution_plan(db: Session, project_id: UUID, current_user: User) -> Project:
    project = get_user_project(db, project_id, current_user)
    if not project.execution_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution plan has not been generated.",
        )
    return project


def _project_query():
    return select(Project).options(
        selectinload(Project.steps),
        selectinload(Project.job),
        selectinload(Project.assigned_agent),
        selectinload(Project.selected_bid),
        selectinload(Project.review),
    )
