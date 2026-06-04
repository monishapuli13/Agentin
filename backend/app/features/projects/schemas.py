from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.features.common.enums import ProjectStatus, ProjectStepStatus


class ProjectStepPublic(BaseModel):
    id: UUID
    project_id: UUID
    step_index: int
    title: str
    description: str
    status: ProjectStepStatus
    output: str | None
    started_at: datetime | None
    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class ProjectPublic(BaseModel):
    id: UUID
    job_id: UUID
    selected_bid_id: UUID
    assigned_agent_id: UUID
    status: ProjectStatus
    execution_plan: dict[str, Any] | None
    execution_result: dict[str, Any] | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    steps: list[ProjectStepPublic] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ProjectExecutionPlanResponse(BaseModel):
    project_id: UUID
    status: ProjectStatus
    execution_plan: dict[str, Any]
    milestones: list[str]
    deliverable_summary: str
    steps: list[ProjectStepPublic]
