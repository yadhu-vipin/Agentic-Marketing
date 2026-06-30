"""Campaign routes — create, retrieve, and run campaigns through the orchestrator."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from marketing_agent.api.dependencies import get_orchestrator
from marketing_agent.orchestrator import MarketingOrchestrator
from marketing_agent.state import CampaignState

router = APIRouter()


# ── Request / Response schemas ────────────────────────────────────────────────

class CreateCampaignRequest(BaseModel):
    name: str
    product_name: str
    product_description: str
    platforms: list[str] = []
    target_audience: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None


class RunCampaignRequest(BaseModel):
    workflow: str   # "organic_campaign" | "lead_generation" | "content_only" | "performance_campaign"


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("", response_model=CampaignState, status_code=201)
async def create_campaign(body: CreateCampaignRequest) -> CampaignState:
    """Create a new campaign record (in-memory for now)."""
    return CampaignState(**body.model_dump())


@router.get("/{campaign_id}", response_model=CampaignState)
async def get_campaign(campaign_id: str) -> CampaignState:
    """Retrieve a campaign by ID. Requires persistent storage (Phase 2)."""
    # TODO (Phase 2): load from database / storage service
    raise HTTPException(
        status_code=501,
        detail="Persistent campaign retrieval requires database setup (Phase 2).",
    )


@router.post("/{campaign_id}/run", response_model=CampaignState)
async def run_campaign(
    campaign_id: str,
    body: RunCampaignRequest,
    create_body: CreateCampaignRequest,
    orchestrator: MarketingOrchestrator = Depends(get_orchestrator),
) -> CampaignState:
    """
    Execute a workflow against the campaign.
    Combines create + run in a single step for MVP convenience.
    """
    state = CampaignState(
        campaign_id=campaign_id,
        **create_body.model_dump(),
    )
    try:
        result = await orchestrator.run(body.workflow, state)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return result


@router.get("", response_model=list[str])
async def list_workflows(
    orchestrator: MarketingOrchestrator = Depends(get_orchestrator),
) -> list[str]:
    """Return all registered workflow names."""
    return orchestrator.available_workflows()
