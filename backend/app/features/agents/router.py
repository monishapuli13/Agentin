from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.schemas import ApiResponse, api_response
from app.features.agents.schemas import AgentDetail, AgentSummary
from app.features.agents.service import get_agent_by_id_or_slug, list_agents

router = APIRouter()


@router.get("", response_model=ApiResponse[list[AgentSummary]])
def agents_index(
    specialization: str | None = None,
    skill: str | None = None,
    min_reputation: float = 0,
    sort: str = "reputation",
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    agents = list_agents(
        db,
        specialization=specialization,
        skill=skill,
        min_reputation=min_reputation,
        sort=sort,
        limit=limit,
        offset=offset,
    )
    return api_response([AgentSummary.model_validate(agent) for agent in agents])


@router.get("/{agent_id_or_slug}", response_model=ApiResponse[AgentDetail])
def agents_show(agent_id_or_slug: str, db: Session = Depends(get_db)):
    agent = get_agent_by_id_or_slug(db, agent_id_or_slug)
    return api_response(AgentDetail.model_validate(agent))

