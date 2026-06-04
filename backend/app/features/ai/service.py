import json
from decimal import Decimal
from typing import Any

from openai import OpenAI

from app.core.config import settings
from app.features.agents.models import Agent
from app.features.ai.schemas import (
    GENERATED_BID_JSON_SCHEMA,
    GENERATED_EXECUTION_PLAN_JSON_SCHEMA,
    GeneratedBid,
    GeneratedExecutionPlan,
    GeneratedExecutionStep,
)
from app.features.bids.models import Bid
from app.features.jobs.models import Job


def generate_bid_with_ai(
    agent: Agent,
    job: Job,
    skill_match: dict[str, Any],
) -> GeneratedBid:
    if not settings.openai_api_key:
        return generate_fallback_bid(agent, job, skill_match)


def generate_execution_plan_with_ai(
    agent: Agent,
    job: Job,
    bid: Bid,
) -> GeneratedExecutionPlan:
    if not settings.openai_api_key:
        return generate_fallback_execution_plan(agent, job, bid)

    try:
        return _generate_openai_execution_plan(agent, job, bid)
    except Exception:
        return generate_fallback_execution_plan(agent, job, bid)

    try:
        return _generate_openai_bid(agent, job, skill_match)
    except Exception:
        return generate_fallback_bid(agent, job, skill_match)


def _generate_openai_bid(
    agent: Agent,
    job: Job,
    skill_match: dict[str, Any],
) -> GeneratedBid:
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.responses.create(
        model=settings.openai_model,
        input=[
            {
                "role": "system",
                "content": (
                    "You are an autonomous AI agent on Agently. "
                    "Generate a realistic freelance bid. Return only data that "
                    "matches the provided schema."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "agent": {
                            "name": agent.name,
                            "headline": agent.headline,
                            "personality": agent.personality,
                            "specialization": agent.specialization,
                            "skills": agent.skills,
                            "reputation_score": str(agent.reputation_score),
                        },
                        "job": {
                            "title": job.title,
                            "description": job.description,
                            "budget_cents": job.budget_cents,
                            "category": job.category,
                            "required_skills": job.required_skills,
                            "deadline_at": job.deadline_at.isoformat()
                            if job.deadline_at
                            else None,
                        },
                        "skill_match": skill_match,
                    }
                ),
            },
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "agently_generated_bid",
                "schema": GENERATED_BID_JSON_SCHEMA,
                "strict": True,
            }
        },
    )

    output_text = getattr(response, "output_text", None)
    if not output_text:
        raise ValueError("OpenAI response did not include output_text.")

    return _normalize_generated_bid(GeneratedBid.model_validate_json(output_text), job)


def _generate_openai_execution_plan(
    agent: Agent,
    job: Job,
    bid: Bid,
) -> GeneratedExecutionPlan:
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.responses.create(
        model=settings.openai_model,
        input=[
            {
                "role": "system",
                "content": (
                    "You are the winning autonomous AI agent on Agently. "
                    "Generate a structured execution plan that is concrete, "
                    "client-readable, and scoped to the selected job."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "agent": {
                            "name": agent.name,
                            "headline": agent.headline,
                            "personality": agent.personality,
                            "specialization": agent.specialization,
                            "skills": agent.skills,
                        },
                        "job": {
                            "title": job.title,
                            "description": job.description,
                            "budget_cents": job.budget_cents,
                            "category": job.category,
                            "required_skills": job.required_skills,
                        },
                        "winning_bid": {
                            "amount_cents": bid.amount_cents,
                            "estimated_hours": str(bid.estimated_hours),
                            "proposal": bid.proposal,
                            "reasoning": bid.reasoning,
                        },
                    }
                ),
            },
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "agently_execution_plan",
                "schema": GENERATED_EXECUTION_PLAN_JSON_SCHEMA,
                "strict": True,
            }
        },
    )

    output_text = getattr(response, "output_text", None)
    if not output_text:
        raise ValueError("OpenAI response did not include output_text.")

    return _normalize_execution_plan(GeneratedExecutionPlan.model_validate_json(output_text))


def generate_fallback_bid(
    agent: Agent,
    job: Job,
    skill_match: dict[str, Any],
) -> GeneratedBid:
    score = Decimal(str(skill_match.get("score", 0.65)))
    reputation = Decimal(str(agent.reputation_score or 0))
    confidence = min(97.0, max(52.0, float((score * 72) + (reputation * 5))))
    bid_factor = Decimal("0.58") + (score * Decimal("0.18"))
    amount = int(Decimal(job.budget_cents) * bid_factor)
    amount = max(5000, min(job.budget_cents, amount))
    estimated_hours = max(4.0, round((job.budget_cents / 10000) * (1.05 - float(score) / 4), 1))
    matched_skills = skill_match.get("matched_skills", [])

    proposal = (
        f"{agent.name} can take on '{job.title}' with a {agent.specialization} "
        "approach. I will focus on the highest-impact requirements first"
    )
    if matched_skills:
        proposal += f", especially {', '.join(matched_skills[:3])}"
    proposal += "."

    reasoning = (
        f"Skill match score {float(score):.2f}; relevant profile strengths include "
        f"{', '.join(matched_skills[:3]) if matched_skills else agent.specialization}."
    )

    return GeneratedBid(
        amount_cents=amount,
        estimated_hours=estimated_hours,
        proposal=proposal,
        confidence_score=round(confidence, 2),
        reasoning=reasoning,
    )


def generate_fallback_execution_plan(
    agent: Agent,
    job: Job,
    bid: Bid,
) -> GeneratedExecutionPlan:
    core_skills = job.required_skills[:3] or [agent.specialization]
    scope = ", ".join(core_skills)
    steps = [
        GeneratedExecutionStep(
            title="Clarify scope and acceptance criteria",
            description=(
                f"Review '{job.title}' and translate the client's request into "
                "concrete implementation checkpoints."
            ),
            output="Scope, constraints, and acceptance criteria are documented.",
        ),
        GeneratedExecutionStep(
            title="Produce the core solution",
            description=(
                f"Apply {agent.name}'s {agent.specialization} expertise to deliver "
                f"the main work, with emphasis on {scope}."
            ),
            output="Core solution plan is completed and mapped to requested skills.",
        ),
        GeneratedExecutionStep(
            title="Review and package the result",
            description=(
                "Validate the work against the bid proposal and prepare a concise "
                "client-facing delivery summary."
            ),
            output="Final delivery summary is ready for client review.",
        ),
    ]

    return GeneratedExecutionPlan(
        execution_plan=(
            f"{agent.name} will execute '{job.title}' in three focused phases: "
            "scope clarification, core production, and final review."
        ),
        milestones=[
            "Scope confirmed",
            "Core solution planned",
            "Review package prepared",
        ],
        deliverable_summary=(
            f"A structured delivery package for '{job.title}', aligned to the "
            f"winning bid of {bid.amount_cents} cents and ready for review."
        ),
        steps=steps,
    )


def _normalize_generated_bid(generated_bid: GeneratedBid, job: Job) -> GeneratedBid:
    generated_bid.amount_cents = max(5000, min(job.budget_cents, generated_bid.amount_cents))
    generated_bid.estimated_hours = round(max(1.0, generated_bid.estimated_hours), 2)
    generated_bid.confidence_score = round(
        max(0.0, min(100.0, generated_bid.confidence_score)),
        2,
    )
    return generated_bid


def _normalize_execution_plan(plan: GeneratedExecutionPlan) -> GeneratedExecutionPlan:
    if len(plan.steps) < 1:
        raise ValueError("Execution plan must include at least one step.")
    if len(plan.milestones) < 1:
        raise ValueError("Execution plan must include at least one milestone.")
    return plan
