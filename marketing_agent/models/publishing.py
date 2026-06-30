"""Publishing models — PublishRequest and PublishResult."""

from typing import TYPE_CHECKING, Optional
from pydantic import BaseModel

if TYPE_CHECKING:
    from marketing_agent.models.content import ContentAsset


class PublishRequest(BaseModel):
    asset: "ContentAsset"           # type: ignore[type-arg]
    scheduled_time: Optional[str] = None


class PublishResult(BaseModel):
    external_id: str
    platform: str
    scheduled: bool = False
