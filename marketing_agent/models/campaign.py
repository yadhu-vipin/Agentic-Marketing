from enum import Enum
from datetime import datetime
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from pydantic import BaseModel

from sqlalchemy import Column, String, JSON, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from marketing_agent.services.storage.postgres_storage import Base

if TYPE_CHECKING:
    from marketing_agent.models.product import ProductModel


class CampaignStatus(str, Enum):
    DRAFT = "draft"
    RESEARCHING = "researching"
    READY = "ready"
    RUNNING = "running"
    FAILED = "failed"

class CampaignModel(Base):
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    product_name = Column(String, nullable=False, default="")
    platforms = Column(JSON, nullable=False, default=list)
    status = Column(String, nullable=False, default="draft")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    workflow = Column(String, nullable=False, default="organic_campaign")
    config = Column(JSON, nullable=False, default=dict)
    results = Column(JSON, nullable=False, default=dict)

    product = relationship("ProductModel", backref="campaigns")

class CampaignResponse(BaseModel):
    campaign_id: str
    workflow_name: str
    created_at: datetime
    product_name: str
    product_description: str
    target_audience: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    platforms: List[str] = []
    scrapers: List[str] = []
    image_mode: str = "none"
    instructions: str = ""
    leads: List[Any] = []
    assets: List[Any] = []
    research_summary: Optional[str] = None
    research_report: Optional[Dict[str, Any]] = None
    status: str
    errors: List[str] = []
    log: List[str] = []

    @classmethod
    def from_orm_model(cls, campaign: CampaignModel) -> "CampaignResponse":
        config_data = campaign.config.get("data", {}) if campaign.config else {}
        results_data = campaign.results if campaign.results else {}
        
        product_desc = ""
        product_ind = ""
        product_target = None
        if campaign.product:
            product_desc = campaign.product.description or ""
            product_ind = campaign.product.industry or ""
            product_target = campaign.product.target_audience
            
        target_audience = config_data.get("target_audience") or product_target
        
        return cls(
            campaign_id=str(campaign.id),
            workflow_name=campaign.workflow,
            created_at=campaign.created_at,
            product_name=campaign.product_name or (campaign.product.name if campaign.product else ""),
            product_description=product_desc,
            target_audience=target_audience,
            industry=product_ind,
            location=config_data.get("location"),
            platforms=campaign.platforms or [],
            scrapers=config_data.get("scrapers", []),
            image_mode=config_data.get("image_mode", "none"),
            instructions=config_data.get("instructions", ""),
            leads=results_data.get("leads", []),
            assets=results_data.get("assets", []),
            research_summary=results_data.get("research_summary"),
            research_report=results_data.get("research_report"),
            status=campaign.status,
            errors=results_data.get("errors", []),
            log=results_data.get("log", []),
        )
