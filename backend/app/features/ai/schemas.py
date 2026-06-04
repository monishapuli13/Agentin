from pydantic import BaseModel, Field


class GeneratedBid(BaseModel):
    amount_cents: int = Field(gt=0)
    estimated_hours: float = Field(gt=0)
    proposal: str = Field(min_length=1)
    confidence_score: float = Field(ge=0, le=100)
    reasoning: str = Field(min_length=1)


class GeneratedExecutionStep(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    output: str = Field(min_length=1)


class GeneratedExecutionPlan(BaseModel):
    execution_plan: str = Field(min_length=1)
    milestones: list[str] = Field(min_length=1)
    deliverable_summary: str = Field(min_length=1)
    steps: list[GeneratedExecutionStep] = Field(min_length=1)


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

GENERATED_EXECUTION_PLAN_JSON_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "execution_plan": {"type": "string"},
        "milestones": {
            "type": "array",
            "items": {"type": "string"},
        },
        "deliverable_summary": {"type": "string"},
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "output": {"type": "string"},
                },
                "required": ["title", "description", "output"],
            },
        },
    },
    "required": [
        "execution_plan",
        "milestones",
        "deliverable_summary",
        "steps",
    ],
}
