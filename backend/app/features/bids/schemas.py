from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.features.agents.schemas import AgentSummary
from app.features.common.enums import BidStatus


class BidPublic(BaseModel):
    id: UUID
    job_id: UUID
    agent_id: UUID
    amount_cents: int
    estimated_hours: Decimal
    proposal: str
    confidence_score: Decimal
    reasoning: str
    skill_match: dict[str, Any]
    status: BidStatus
    created_at: datetime
    agent: AgentSummary | None = None

    model_config = ConfigDict(from_attributes=True)

