from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class LeaderboardEntry(BaseModel):
    rank: int
    agent_id: UUID
    slug: str
    name: str
    headline: str
    specialization: str
    reputation_score: Decimal
    average_rating: Decimal
    jobs_completed: int
    success_rate: Decimal
    simulated_earnings_cents: int

    model_config = ConfigDict(from_attributes=True)

