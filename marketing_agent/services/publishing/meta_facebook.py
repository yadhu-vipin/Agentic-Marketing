"""
MetaFacebookPublisher — publishes photo posts to a Facebook Page.

Verified flow: POST /{page_id}/photos via graph.facebook.com
Token: META_ACCESS_TOKEN (Page Access Token)

Source of truth: apps/web/lib/meta/publish.ts → publishFacebook()
"""

import logging
from urllib.parse import urlencode

import httpx

from marketing_agent.configs.settings import get_settings
from marketing_agent.models.publishing import PublishRequest, PublishResult
from marketing_agent.services.publishing.base import PublisherService

logger = logging.getLogger(__name__)


class MetaFacebookPublisher(PublisherService):
    platform = "facebook"

    def __init__(self) -> None:
        s = get_settings()
        self._token = s.meta_access_token
        self._page_id = s.meta_page_id
        self._version = s.meta_graph_version
        self._base = f"https://graph.facebook.com/{self._version}"

    def _caption(self, asset) -> str:
        tags = " ".join(f"#{h.lstrip('#')}" for h in asset.hashtags)
        return "\n\n".join(filter(None, [asset.body, asset.cta, tags]))

    async def publish(self, request: PublishRequest) -> PublishResult:
        if not self._token or not self._page_id:
            raise RuntimeError(
                "META_ACCESS_TOKEN and META_PAGE_ID must be set for Facebook publishing."
            )
        asset = request.asset
        if not asset.creative_url:
            raise ValueError("No creative_url on asset — cannot publish to Facebook.")

        params: dict = {
            "url": asset.creative_url,
            "caption": self._caption(asset),
            "access_token": self._token,
        }

        if request.scheduled_time:
            import math, datetime as dt
            epoch = math.floor(
                dt.datetime.fromisoformat(request.scheduled_time).timestamp()
            )
            params["published"] = "false"
            params["scheduled_publish_time"] = str(epoch)

        url = f"{self._base}/{self._page_id}/photos"
        logger.info("[MetaFacebookPublisher] POST %s", url)

        async with httpx.AsyncClient() as client:
            res = await client.post(url, data=params)
            data = res.json()

        if not res.is_success:
            err = data.get("error", {})
            raise RuntimeError(
                f"Facebook publish failed ({res.status_code}): {err.get('message', data)}"
            )

        external_id = str(data.get("post_id") or data.get("id", ""))
        logger.info("[MetaFacebookPublisher] published id=%s", external_id)
        return PublishResult(
            external_id=external_id,
            platform=self.platform,
            scheduled=bool(request.scheduled_time),
        )
