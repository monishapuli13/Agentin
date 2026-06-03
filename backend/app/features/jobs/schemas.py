from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.features.bids.schemas import BidPublic
from app.features.common.enums import JobStatus


class JobCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10)
    budget_cents: int = Field(ge=5000)
    category: str | None = Field(default=None, max_length=100)
    required_skills: list[str] = Field(default_factory=list)
    deadline_at: datetime | None = None


class JobPublic(BaseModel):
    id: UUID
    client_id: UUID
    title: str
    description: str
    budget_cents: int
    category: str | None
    required_skills: list[str]
    deadline_at: datetime | None
    status: JobStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobCreateResponse(BaseModel):
    job: JobPublic
    bids_generated: int


class SelectWinningBidResponse(BaseModel):
    job: JobPublic
    selected_bid: BidPublic
    project_id: UUID

