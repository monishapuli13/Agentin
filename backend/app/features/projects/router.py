from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.schemas import ApiResponse, api_response
from app.features.auth.dependencies import get_current_user
from app.features.auth.models import User
from app.features.projects.schemas import ProjectExecutionPlanResponse, ProjectPublic, ProjectStepPublic
from app.features.projects.service import (
    get_project_execution_plan,
    get_user_project,
    list_user_projects,
)

router = APIRouter()


@router.get("", response_model=ApiResponse[list[ProjectPublic]])
def projects_index(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    projects = list_user_projects(db, current_user)
    return api_response([ProjectPublic.model_validate(project) for project in projects])


@router.get("/{project_id}", response_model=ApiResponse[ProjectPublic])
def projects_show(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = get_user_project(db, project_id, current_user)
    return api_response(ProjectPublic.model_validate(project))


@router.get(
    "/{project_id}/execution-plan",
    response_model=ApiResponse[ProjectExecutionPlanResponse],
)
def projects_execution_plan(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = get_project_execution_plan(db, project_id, current_user)
    execution_result = project.execution_result or {}
    return api_response(
        ProjectExecutionPlanResponse(
            project_id=project.id,
            status=project.status,
            execution_plan=project.execution_plan or {},
            milestones=(project.execution_plan or {}).get("milestones", []),
            deliverable_summary=execution_result.get("deliverable_summary", ""),
            steps=[ProjectStepPublic.model_validate(step) for step in project.steps],
        )
    )
