"""AnalyticsCapability — placeholder for post-publish Meta Insights reporting."""

import logging
from marketing_agent.capabilities.base import Capability
from marketing_agent.state import CampaignState

logger = logging.getLogger(__name__)


class AnalyticsCapability(Capability):
    """
    Placeholder — reads post-publish stats from Meta Insights API.
    Implement after publishing is stable.
    """
    name = "analytics"

    async def _execute(self, state: CampaignState) -> CampaignState:
        logger.info(
            "[AnalyticsCapability] not yet implemented — skipping for campaign=%s",
            state.campaign_id,
        )
        state.add_log("analytics: placeholder — no data collected")
        return state
