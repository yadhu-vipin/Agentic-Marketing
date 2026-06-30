"""
MetaInstagramPublisher — publishes image posts to an Instagram Business account.

Verified flow (graph.instagram.com, INSTAGRAM_ACCESS_TOKEN):
  1. GET  /me                       → discover ig_user_id (skipped if configured)
  2. POST /{ig_user_id}/media       → create container
  3. POST /{ig_user_id}/media_publish → publish

Source of truth: apps/web/lib/meta/publish.ts → publishInstagram()
"""

import logging

import httpx

from marketing_agent.configs.settings import get_settings
from marketing_agent.models.publishing import PublishRequest, PublishResult
from marketing_agent.services.publishing.base import PublisherService

logger = logging.getLogger(__name__)


class MetaInstagramPublisher(PublisherService):
    platform = "instagram"

    def __init__(self) -> None:
        s = get_settings()
        self._token = s.instagram_access_token or s.meta_access_token
        self._ig_user_id = s.meta_ig_user_id
        self._version = s.meta_graph_version
        self._base = f"https://graph.instagram.com/{self._version}"

    def _caption(self, asset) -> str:
        tags = " ".join(f"#{h.lstrip('#')}" for h in asset.hashtags)
        return "\n\n".join(filter(None, [asset.body, asset.cta, tags]))

    async def _resolve_ig_user_id(self, client: httpx.AsyncClient) -> str:
        if self._ig_user_id:
            return self._ig_user_id
        logger.info("[MetaInstagramPublisher] discovering ig_user_id via /me")
        res = await client.get(
            f"{self._base}/me",
            params={"access_token": self._token},
        )
        data = res.json()
        if not res.is_success or "id" not in data:
            raise RuntimeError(
                f"Instagram /me failed ({res.status_code}): {data}. "
                "Set META_IG_USER_ID in .env to skip discovery."
            )
        return str(data["id"])

    async def publish(self, request: PublishRequest) -> PublishResult:
        if not self._token:
            raise RuntimeError(
                "INSTAGRAM_ACCESS_TOKEN (or META_ACCESS_TOKEN) must be set."
            )
        asset = request.asset
        if not asset.creative_url:
            raise ValueError("No creative_url on asset — cannot publish to Instagram.")

        async with httpx.AsyncClient() as client:
            ig_user_id = await self._resolve_ig_user_id(client)

            # Step 1: create container
            logger.info(
                "[MetaInstagramPublisher] POST %s/%s/media", self._base, ig_user_id
            )
            container_res = await client.post(
                f"{self._base}/{ig_user_id}/media",
                data={
                    "image_url": asset.creative_url,
                    "caption": self._caption(asset),
                    "access_token": self._token,
                },
            )
            container = container_res.json()
            if not container_res.is_success or "id" not in container:
                err = container.get("error", {})
                raise RuntimeError(
                    f"Instagram /media failed ({container_res.status_code}): "
                    f"{err.get('message', container)}"
                )
            creation_id = container["id"]
            logger.info("[MetaInstagramPublisher] container id=%s", creation_id)

            # Step 2: publish container
            publish_res = await client.post(
                f"{self._base}/{ig_user_id}/media_publish",
                data={"creation_id": creation_id, "access_token": self._token},
            )
            published = publish_res.json()
            if not publish_res.is_success:
                err = published.get("error", {})
                raise RuntimeError(
                    f"Instagram /media_publish failed ({publish_res.status_code}): "
                    f"{err.get('message', published)}"
                )

        external_id = str(published.get("id", ""))
        logger.info("[MetaInstagramPublisher] published id=%s", external_id)
        return PublishResult(
            external_id=external_id,
            platform=self.platform,
            scheduled=False,
        )
