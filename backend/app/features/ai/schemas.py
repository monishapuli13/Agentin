from pydantic import BaseModel, Field


class GeneratedBid(BaseModel):
    amount_cents: int = Field(gt=0)
    estimated_hours: float = Field(gt=0)
    proposal: str = Field(min_length=1)
    confidence_score: float = Field(ge=0, le=100)
    reasoning: str = Field(min_length=1)


GENERATED_BID_JSON_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "amount_cents": {"type": "integer"},
        "estimated_hours": {"type": "number"},
        "proposal": {"type": "string"},
        "confidence_score": {"type": "number"},
        "reasoning": {"type": "string"},
    },
    "required": [
        "amount_cents",
        "estimated_hours",
        "proposal",
        "confidence_score",
        "reasoning",
    ],
}

