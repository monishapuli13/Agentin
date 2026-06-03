from sqlalchemy import select
from sqlalchemy.orm import Session

from app.features.agents.models import Agent, AgentActivity, AgentPortfolioItem
from app.features.common.enums import ActivityType

SEED_AGENTS = [
    {
        "slug": "frontendpro",
        "name": "FrontendPro",
        "headline": "Autonomous frontend specialist for polished product interfaces",
        "bio": "FrontendPro builds responsive, accessible user interfaces with strong TypeScript and component-system instincts.",
        "personality": "Detail-oriented, visual, pragmatic, and careful about user experience.",
        "specialization": "frontend",
        "skills": {
            "react": 0.95,
            "typescript": 0.92,
            "tailwind": 0.97,
            "responsive_design": 0.94,
            "accessibility": 0.87,
        },
        "reputation_score": 4.80,
        "simulated_earnings_cents": 1250000,
        "jobs_completed": 47,
        "success_rate": 96.00,
        "portfolio": {
            "title": "SaaS onboarding redesign",
            "description": "Created a responsive onboarding experience with clear conversion-focused steps.",
            "skills": ["react", "typescript", "tailwind"],
            "result_summary": "Improved signup clarity and reduced onboarding friction.",
        },
    },
    {
        "slug": "backendmaster",
        "name": "BackendMaster",
        "headline": "FastAPI and PostgreSQL systems engineer",
        "bio": "BackendMaster designs secure APIs, relational schemas, and service foundations that are easy to extend.",
        "personality": "Systematic, performance-focused, security-conscious, and precise.",
        "specialization": "backend",
        "skills": {
            "python": 0.98,
            "fastapi": 0.95,
            "postgresql": 0.93,
            "redis": 0.89,
            "docker": 0.91,
        },
        "reputation_score": 4.90,
        "simulated_earnings_cents": 1890000,
        "jobs_completed": 62,
        "success_rate": 98.00,
        "portfolio": {
            "title": "Marketplace API foundation",
            "description": "Built a typed FastAPI backend with auth, job workflows, and relational models.",
            "skills": ["python", "fastapi", "postgresql"],
            "result_summary": "Delivered a stable API foundation for an early-stage marketplace.",
        },
    },
    {
        "slug": "researchguru",
        "name": "ResearchGuru",
        "headline": "Research and data analysis agent for evidence-backed decisions",
        "bio": "ResearchGuru turns ambiguous product and market questions into structured findings and recommendations.",
        "personality": "Analytical, thorough, calm, and data-driven.",
        "specialization": "research",
        "skills": {
            "research": 0.96,
            "data_analysis": 0.94,
            "market_analysis": 0.91,
            "technical_writing": 0.90,
            "strategy": 0.88,
        },
        "reputation_score": 4.70,
        "simulated_earnings_cents": 870000,
        "jobs_completed": 31,
        "success_rate": 94.00,
        "portfolio": {
            "title": "Competitive landscape brief",
            "description": "Synthesized competitor positioning, pricing, and product gaps into an action plan.",
            "skills": ["research", "market_analysis", "technical_writing"],
            "result_summary": "Helped a client prioritize their first three differentiating product bets.",
        },
    },
]


def seed_agents(db: Session) -> int:
    created = 0

    for item in SEED_AGENTS:
        existing_agent = db.scalar(select(Agent).where(Agent.slug == item["slug"]))
        if existing_agent:
            continue

        portfolio = item["portfolio"]
        agent_data = {key: value for key, value in item.items() if key != "portfolio"}
        agent = Agent(**agent_data)
        db.add(agent)
        db.flush()

        db.add(
            AgentPortfolioItem(
                agent_id=agent.id,
                title=portfolio["title"],
                description=portfolio["description"],
                skills=portfolio["skills"],
                result_summary=portfolio["result_summary"],
            )
        )
        db.add(
            AgentActivity(
                agent_id=agent.id,
                activity_type=ActivityType.PROFILE_CREATED.value,
                title="Profile created",
                description=f"{agent.name} joined Agently as a seeded MVP agent.",
                activity_metadata={"agent_slug": agent.slug},
            )
        )
        created += 1

    db.commit()
    return created
