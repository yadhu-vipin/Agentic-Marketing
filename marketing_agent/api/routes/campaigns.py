"""Campaign resource routes — RESTful campaign state management."""

from typing import Optional
import asyncio

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel

from marketing_agent.api.dependencies import get_orchestrator, get_storage
from marketing_agent.orchestrator import MarketingOrchestrator
from marketing_agent.state import CampaignState
from marketing_agent.services.storage.base import StorageService

from research.orchestrator.workflow import ResearchWorkflow
from research.providers import ProviderRegistry
from research.providers.gemini.gemini_service import GeminiLLMService
from research.orchestrator.executor import ResearchExecutor
from research.orchestrator.aggregator import ResultAggregator

router = APIRouter()


# ── Request Schemas ───────────────────────────────────────────────────────────

class CreateCampaignRequest(BaseModel):
    id: str
    name: str
    workflow: str
    config: dict


class UpdateCampaignRequest(BaseModel):
    name: Optional[str] = None
    workflow: Optional[str] = None
    config: Optional[dict] = None


# ── Helper ────────────────────────────────────────────────────────────────────

def map_config_to_state(state: CampaignState, config: dict) -> None:
    """Map dynamic configuration parameters into the CampaignState model."""
    if "product_name" in config:
        state.product_name = config["product_name"]
    if "product_description" in config:
        state.product_description = config["product_description"]
    if "target_audience" in config:
        state.target_audience = config["target_audience"]
    if "industry" in config:
        state.industry = config["industry"]
    if "location" in config:
        state.location = config["location"]
    if "platforms" in config:
        state.platforms = config["platforms"]
    if "scrapers" in config:
        state.scrapers = config["scrapers"]
    if "image_mode" in config:
        state.image_mode = config["image_mode"]
    if "instructions" in config:
        state.instructions = config["instructions"]


async def execute_serp_research(product_name: str, target_audience: str) -> dict:
    """Helper to run the research subsystem standalone for the UI."""
    registry = ProviderRegistry()
    registry.register_llm(GeminiLLMService())
    
    executor = ResearchExecutor(registry)
    aggregator = ResultAggregator(registry)
    workflow = ResearchWorkflow(executor, aggregator)
    
    context = {
        "product_name": product_name,
        "target_audience": target_audience,
    }
    
    report = await workflow.run(context)
    return report


async def run_research_task(campaign_id: str, state: CampaignState, storage: StorageService):
    """Background task to run research and update state."""
    state.status = "researching"
    await storage.save(f"campaign_{campaign_id}", state.model_dump(mode="json"))
    
    try:
        report = await execute_serp_research(
            product_name=state.product_name,
            target_audience=state.target_audience or "General audience"
        )
        state.research_report = report
        state.status = "draft"  # Return to draft or idle state after research
        state.add_log("Research completed successfully.")
    except Exception as e:
        state.fail(f"Research failed: {str(e)}")
        
    await storage.save(f"campaign_{campaign_id}", state.model_dump(mode="json"))


async def run_campaign_workflow_task(
    campaign_id: str,
    state: CampaignState,
    orchestrator: MarketingOrchestrator,
    storage: StorageService
):
    try:
        result = await orchestrator.run(state.workflow_name, state)
        await storage.save(f"campaign_{campaign_id}", result.model_dump(mode="json"))
    except ValueError as exc:
        state.fail(str(exc))
        await storage.save(f"campaign_{campaign_id}", state.model_dump(mode="json"))
    except Exception as exc:
        state.fail(f"Unhandled error during execution: {str(exc)}")
        await storage.save(f"campaign_{campaign_id}", state.model_dump(mode="json"))


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("", response_model=CampaignState, status_code=201)
async def create_campaign(
    body: CreateCampaignRequest,
    storage: StorageService = Depends(get_storage),
) -> CampaignState:
    """Create a persistent campaign and store workflow and config parameters."""
    state = CampaignState(
        campaign_id=body.id,
        workflow_name=body.workflow,
        product_name=body.name,
        status="draft"
    )
    map_config_to_state(state, body.config)

    await storage.save(f"campaign_{body.id}", state.model_dump(mode="json"))
    return state


@router.get("/{campaign_id}", response_model=CampaignState)
async def get_campaign(
    campaign_id: str,
    storage: StorageService = Depends(get_storage),
) -> CampaignState:
    """Retrieve metadata, config, status, and results for a campaign."""
    data = await storage.load(f"campaign_{campaign_id}")
    if not data:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return CampaignState(**data)


@router.patch("/{campaign_id}", response_model=CampaignState)
async def update_campaign(
    campaign_id: str,
    body: UpdateCampaignRequest,
    storage: StorageService = Depends(get_storage),
) -> CampaignState:
    """Update campaign metadata and configuration."""
    data = await storage.load(f"campaign_{campaign_id}")
    if not data:
        raise HTTPException(status_code=404, detail="Campaign not found")

    state = CampaignState(**data)
    if body.name is not None:
        state.product_name = body.name
    if body.workflow is not None:
        state.workflow_name = body.workflow
    if body.config is not None:
        map_config_to_state(state, body.config)

    await storage.save(f"campaign_{campaign_id}", state.model_dump(mode="json"))
    return state


@router.post("/{campaign_id}/run", response_model=CampaignState)
async def run_campaign(
    campaign_id: str,
    background_tasks: BackgroundTasks,
    orchestrator: MarketingOrchestrator = Depends(get_orchestrator),
    storage: StorageService = Depends(get_storage),
) -> CampaignState:
    """Execute the configured campaign workflow using stored inputs."""
    data = await storage.load(f"campaign_{campaign_id}")
    if not data:
        raise HTTPException(status_code=404, detail="Campaign not found")

    state = CampaignState(**data)
    state.status = "running"
    state.add_log(f"Starting execution of workflow: {state.workflow_name}")
    await storage.save(f"campaign_{campaign_id}", state.model_dump(mode="json"))

    background_tasks.add_task(run_campaign_workflow_task, campaign_id, state, orchestrator, storage)
    return state


@router.post("/{campaign_id}/research", response_model=CampaignState)
async def run_campaign_research(
    campaign_id: str,
    background_tasks: BackgroundTasks,
    storage: StorageService = Depends(get_storage),
) -> CampaignState:
    """Trigger the research phase for a campaign in the background."""
    data = await storage.load(f"campaign_{campaign_id}")
    if not data:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    state = CampaignState(**data)
    background_tasks.add_task(run_research_task, campaign_id, state, storage)
    
    return state
