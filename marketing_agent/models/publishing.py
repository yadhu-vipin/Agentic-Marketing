"""Publishing models — PublishRequest and PublishResult."""

from typing import Optional
from pydantic import BaseModel

from marketing_agent.models.content import ContentAsset


class PublishRequest(BaseModel):
    asset: ContentAsset
    scheduled_time: Optional[str] = None


class PublishResult(BaseModel):
    external_id: str
    platform: str
    scheduled: bool = False

