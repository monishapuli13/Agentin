from decimal import Decimal
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

