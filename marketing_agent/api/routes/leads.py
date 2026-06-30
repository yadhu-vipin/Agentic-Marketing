"""Lead discovery routes."""

from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from marketing_agent.api.dependencies import get_orchestrator
from marketing_agent.orchestrator import MarketingOrchestrator
from marketing_agent.state import CampaignState

router = APIRouter()


class DiscoverLeadsRequest(BaseModel):
    product_description: str
    target_audience: Optional[str] = None
    location: Optional[str] = None


@router.post("/discover", response_model=CampaignState)
async def discover_leads(
    body: DiscoverLeadsRequest,
    orchestrator: MarketingOrchestrator = Depends(get_orchestrator),
) -> CampaignState:
    """Run the lead_generation workflow and return the resulting state."""
    state = CampaignState(**body.model_dump())
    return await orchestrator.run("lead_generation", state)
