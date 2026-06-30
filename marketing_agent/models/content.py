"""Content models — ContentRequest and ContentAsset."""

from typing import Optional
from pydantic import BaseModel


class ContentRequest(BaseModel):
    campaign_id: str
    platform: str
    headline: str = ""
    body: str = ""
    hashtags: list[str] = []
    cta: str = ""
    creative_prompt: str = ""


class ContentAsset(BaseModel):
    campaign_id: str
    platform: str
    headline: str = ""
    body: str = ""
    hashtags: list[str] = []
    cta: str = ""
    creative_prompt: str = ""
    creative_url: Optional[str] = None
    status: str = "draft"
