"""ContentCapability — generates copy and creative prompts per platform."""

import logging
from marketing_agent.capabilities.base import Capability
from marketing_agent.models.content import ContentAsset
from marketing_agent.services.llm.base import LLMService
from marketing_agent.state import CampaignState

logger = logging.getLogger(__name__)


class ContentCapability(Capability):
    name = "content"

    def __init__(self, llm: LLMService) -> None:
        self._llm = llm

    async def _execute(self, state: CampaignState) -> CampaignState:
        # Fall back to a simple per-platform loop if planning produced nothing
        plans = state.content_plan or [{"platform": p} for p in state.platforms]
        assets: list[ContentAsset] = []

        for plan in plans:
            platform = plan.get("platform", "instagram")
            prompt = (
                f"Write post copy for {platform}.\n"
                f"Product: {state.product_name}\n"
                f"Description: {state.product_description}\n"
                f"Audience: {state.target_audience or 'general'}\n"
                f"Brief: {plan}\n\n"
                "Return JSON with keys: headline, body, hashtags (list), cta, creative_prompt."
            )
            data = await self._llm.generate_json(prompt)
            assets.append(
                ContentAsset(
                    campaign_id=state.campaign_id,
                    platform=platform,
                    headline=data.get("headline", ""),
                    body=data.get("body", ""),
                    hashtags=data.get("hashtags", []),
                    cta=data.get("cta", ""),
                    creative_prompt=data.get("creative_prompt", ""),
                )
            )

        state.assets = assets
        logger.info("[ContentCapability] generated %d assets", len(assets))
        return state
