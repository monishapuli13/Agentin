from decimal import Decimal
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AgentSummary(BaseModel):
    id: UUID
    slug: str
    name: str
    headline: str
    specialization: str
    skills: dict[str, float]
    reputation_score: Decimal
    average_rating: Decimal
    simulated_earnings_cents: int
    jobs_completed: int
    success_rate: Decimal

    model_config = ConfigDict(from_attributes=True)


class AgentPortfolioItemPublic(BaseModel):
    id: UUID
    title: str
    description: str
    skills: list[str]
    result_summary: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AgentActivityPublic(BaseModel):
    id: UUID
    activity_type: str
    title: str
    description: str
    activity_metadata: dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AgentWorkHistoryItem(BaseModel):
    project_id: UUID
    job_id: UUID
    job_title: str
    rating: int
    quality_score: int
    timeliness_score: int
    comment: str | None
    amount_cents: int
    completed_at: datetime | None


class AgentReputationSummary(BaseModel):
    reputation_score: Decimal
    average_rating: Decimal
    jobs_completed: int
    success_rate: Decimal
    simulated_earnings_cents: int


class AgentDetail(AgentSummary):
    bio: str
    personality: str
    average_response_seconds: int
    portfolio_items: list[AgentPortfolioItemPublic]
    activities: list[AgentActivityPublic]
    work_history: list[AgentWorkHistoryItem]
    completed_projects: int
    earnings_cents: int
    reputation_summary: AgentReputationSummary

    model_config = ConfigDict(from_attributes=True)
