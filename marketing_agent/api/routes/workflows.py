"""Workflow metadata routes."""

from fastapi import APIRouter, Depends

from marketing_agent.api.dependencies import get_orchestrator
from marketing_agent.orchestrator import MarketingOrchestrator

router = APIRouter()


@router.get("", response_model=list[str])
async def list_workflows(
    orchestrator: MarketingOrchestrator = Depends(get_orchestrator),
) -> list[str]:
    """Return all registered workflow names."""
    return orchestrator.available_workflows()
