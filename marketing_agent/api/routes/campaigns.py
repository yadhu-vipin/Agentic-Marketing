"""Campaign resource routes — RESTful campaign state management."""

import logging
from typing import Optional, Any
import asyncio

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from marketing_agent.api.dependencies import get_orchestrator, get_db
from marketing_agent.orchestrator import MarketingOrchestrator
from marketing_agent.state import CampaignState
from marketing_agent.services.storage.postgres_storage import get_session
from marketing_agent.services.storage.campaign_repository import CampaignRepository
from marketing_agent.models import CampaignResponse, CampaignStatus

from research.orchestrator.workflow import ResearchWorkflow
from research.orchestrator import ProviderRegistry
from marketing_agent.services.llm.gemini import GeminiLLMService
from research.orchestrator.executor import ResearchExecutor
from research.orchestrator.aggregator import ResultAggregator
from research.providers.serpapi import SerpAPIProvider
from research.models.context import ResearchContext

logger = logging.getLogger(__name__)

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
    registry.register(SerpAPIProvider())
    
    executor = ResearchExecutor(concurrency_limit=5)
    aggregator = ResultAggregator()
    workflow = ResearchWorkflow(registry, executor, aggregator)
    
    context = ResearchContext(
        product_description=product_name,
        company_name=None,
        industry=None,
        country=None,
        language=None,
        deep_research=False,
        metadata={"target_audience": target_audience}
    )
    
    report = await workflow.run(context)
    return report.model_dump()


async def run_research_task(campaign_id: str):
    """Background task to run research and update the campaigns table."""
    db = get_session()
    repo = CampaignRepository(db)
    try:
        campaign = repo.get_campaign(campaign_id)
        if not campaign:
            logger.error(f"Campaign {campaign_id} not found in background task")
            return

        # Build ResearchContext directly from the campaign and product relation
        product = campaign.product
        product_name = campaign.product_name or (product.name if product else "")
        product_description = product.description if product else ""
        
        config_data = campaign.config.get("data", {}) if campaign.config else {}
        target_audience = config_data.get("target_audience") or (product.target_audience if product else "General audience")

        logger.info(f"Running SerpAPI research for campaign {campaign_id} ({product_name})")

        # Run research workflow
        report = await execute_serp_research(
            product_name=product_name,
            target_audience=target_audience
        )

        # Store research results
        results = {
            "research_report": report
        }
        repo.save_results(campaign_id, results)
        repo.update_campaign(campaign_id, status=CampaignStatus.DRAFT)
        logger.info(f"Research completed successfully for campaign {campaign_id}")
    except Exception as e:
        logger.error(f"Research failed for campaign {campaign_id}: {e}", exc_info=True)
        # Update status to failed
        repo.update_campaign(campaign_id, status=CampaignStatus.FAILED)
        # Store error in results JSON
        repo.save_results(campaign_id, {"errors": [str(e)]})
    finally:
        db.close()


async def run_campaign_workflow_task(
    campaign_id: str,
    state: CampaignState,
    orchestrator: MarketingOrchestrator,
):
    db = get_session()
    repo = CampaignRepository(db)
    try:
        result = await orchestrator.run(state.workflow_name, state)
        repo.save_results(campaign_id, result.model_dump(mode="json"))
        repo.update_campaign(campaign_id, status=CampaignStatus.COMPLETED)
    except ValueError as exc:
        state.fail(str(exc))
        repo.save_results(campaign_id, state.model_dump(mode="json"))
        repo.update_campaign(campaign_id, status=CampaignStatus.FAILED)
    except Exception as exc:
        state.fail(f"Unhandled error during execution: {str(exc)}")
        repo.save_results(campaign_id, state.model_dump(mode="json"))
        repo.update_campaign(campaign_id, status=CampaignStatus.FAILED)
    finally:
        db.close()


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("", response_model=CampaignResponse, status_code=201)
async def create_campaign(
    body: CreateCampaignRequest,
    db: Session = Depends(get_db),
) -> CampaignResponse:
    """Create or register a persistent campaign and store workflow and config parameters."""
    repo = CampaignRepository(db)
    campaign = repo.get_campaign(body.id)
    if not campaign:
        raise HTTPException(
            status_code=404,
            detail=f"Campaign {body.id} not found in the database. Please create it via the frontend first."
        )

    # Update config and status to draft
    campaign = repo.update_campaign(
        body.id,
        workflow=body.workflow,
        config=body.config,
        status=CampaignStatus.DRAFT
    )
    return CampaignResponse.from_orm_model(campaign)


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    db: Session = Depends(get_db),
) -> CampaignResponse:
    """Retrieve metadata, config, status, and results for a campaign."""
    repo = CampaignRepository(db)
    campaign = repo.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return CampaignResponse.from_orm_model(campaign)


@router.patch("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    body: UpdateCampaignRequest,
    db: Session = Depends(get_db),
) -> CampaignResponse:
    """Update campaign metadata and configuration."""
    repo = CampaignRepository(db)
    campaign = repo.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    update_data = {}
    if body.name is not None:
        update_data["product_name"] = body.name
    if body.workflow is not None:
        update_data["workflow"] = body.workflow
    if body.config is not None:
        # Merge config
        current_config = dict(campaign.config) if campaign.config else {}
        current_config.update(body.config)
        update_data["config"] = current_config

    campaign = repo.update_campaign(campaign_id, **update_data)
    return CampaignResponse.from_orm_model(campaign)


@router.post("/{campaign_id}/run", response_model=CampaignResponse)
async def run_campaign(
    campaign_id: str,
    background_tasks: BackgroundTasks,
    orchestrator: MarketingOrchestrator = Depends(get_orchestrator),
    db: Session = Depends(get_db),
) -> CampaignResponse:
    """Execute the configured campaign workflow using stored inputs."""
    repo = CampaignRepository(db)
    campaign = repo.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    state = CampaignState(
        campaign_id=campaign_id,
        workflow_name=campaign.workflow or "default",
        status="running",
        product_name=campaign.product_name or "",
    )
    
    config_data = campaign.config.get("data", {}) if campaign.config else {}
    if config_data:
        map_config_to_state(state, config_data)
        
    state.add_log(f"Starting execution of workflow: {state.workflow_name}")
    
    campaign = repo.update_campaign(campaign_id, status=CampaignStatus.RUNNING)
    background_tasks.add_task(run_campaign_workflow_task, campaign_id, state, orchestrator)
    
    return CampaignResponse.from_orm_model(campaign)


@router.post("/{campaign_id}/research", response_model=CampaignResponse)
async def run_campaign_research(
    campaign_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> CampaignResponse:
    """Trigger the research phase for a campaign in the background."""
    repo = CampaignRepository(db)
    campaign = repo.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    repo.update_campaign(campaign_id, status=CampaignStatus.RESEARCHING)
    background_tasks.add_task(run_research_task, campaign_id)
    
    return CampaignResponse.from_orm_model(campaign)
