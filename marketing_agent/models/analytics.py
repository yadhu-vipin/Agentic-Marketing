"""Analytics models — placeholder for post-MVP insights reporting."""

from typing import Any, Optional
from pydantic import BaseModel


class AnalyticsReport(BaseModel):
    campaign_id: str
    impressions: Optional[int] = None
    reach: Optional[int] = None
    engagement: Optional[int] = None
    clicks: Optional[int] = None
    raw: Optional[Any] = None       # raw API response for future parsing
