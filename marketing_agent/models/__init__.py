"""Shared models package."""

from marketing_agent.models.product import ProductModel
from marketing_agent.models.campaign import CampaignModel, CampaignResponse, CampaignStatus

__all__ = [
    "ProductModel",
    "CampaignModel",
    "CampaignResponse",
    "CampaignStatus",
]
