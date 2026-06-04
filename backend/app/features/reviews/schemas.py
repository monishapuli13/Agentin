from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.features.common.enums import ProjectStatus, ReviewStatus


class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    quality_score: int = Field(ge=1, le=5)
    timeliness_score: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=2000)


class ReviewPublic(BaseModel):
    id: UUID
    project_id: UUID
    client_id: UUID
    agent_id: UUID
    rating: int
    quality_score: int
    timeliness_score: int
    comment: str | None
    status: ReviewStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReputationUpdate(BaseModel):
    agent_id: UUID
    reputation_score: Decimal
    average_rating: Decimal
    jobs_completed: int
    success_rate: Decimal
    simulated_earnings_cents: int


class ReviewCreateResponse(BaseModel):
    review: ReviewPublic
    project_status: ProjectStatus
    reputation: ReputationUpdate

