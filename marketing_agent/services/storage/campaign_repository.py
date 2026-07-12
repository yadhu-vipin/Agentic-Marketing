import uuid
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from marketing_agent.models.campaign import CampaignModel

class CampaignRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_campaign(self, campaign_id: str) -> Optional[CampaignModel]:
        try:
            val = uuid.UUID(campaign_id)
        except ValueError:
            return None
        return self.db.query(CampaignModel).filter(CampaignModel.id == val).first()

    def update_campaign(self, campaign_id: str, **kwargs) -> Optional[CampaignModel]:
        campaign = self.get_campaign(campaign_id)
        if not campaign:
            return None
        for key, value in kwargs.items():
            if hasattr(campaign, key):
                setattr(campaign, key, value)
        self.db.commit()
        return campaign

    def save_results(self, campaign_id: str, results: Dict[str, Any]) -> Optional[CampaignModel]:
        campaign = self.get_campaign(campaign_id)
        if not campaign:
            return None
        # Copy current dict to trigger change detection
        current_results = dict(campaign.results) if campaign.results else {}
        current_results.update(results)
        campaign.results = current_results
        self.db.commit()
        return campaign
