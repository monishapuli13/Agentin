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


class AgentDetail(AgentSummary):
    bio: str
    personality: str
    average_response_seconds: int
    portfolio_items: list[AgentPortfolioItemPublic]
    activities: list[AgentActivityPublic]

    model_config = ConfigDict(from_attributes=True)

