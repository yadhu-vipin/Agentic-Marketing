"""PublishingCapability — publishes ContentAssets via the service layer."""

import logging
from marketing_agent.capabilities.base import Capability
from marketing_agent.models.publishing import PublishRequest
from marketing_agent.services.publishing.base import PublisherService
from marketing_agent.state import CampaignState

logger = logging.getLogger(__name__)


class PublishingCapability(Capability):
    name = "publishing"

    def __init__(self, publishers: dict[str, PublisherService]) -> None:
        """
        publishers: mapping of platform name → PublisherService implementation.
        Example: {"facebook": MetaFacebookPublisher(), "instagram": MetaInstagramPublisher()}
        """
        self._publishers = publishers

    async def _execute(self, state: CampaignState) -> CampaignState:
        results = []
        for asset in state.assets:
            publisher = self._publishers.get(asset.platform)
            if not publisher:
                logger.warning(
                    "[PublishingCapability] no publisher registered for platform: %s",
                    asset.platform,
                )
                state.add_log(f"skipped platform with no publisher: {asset.platform}")
                continue
            result = await publisher.publish(PublishRequest(asset=asset))
            results.append(result)
            logger.info(
                "[PublishingCapability] published %s → %s",
                asset.platform,
                result.external_id,
            )
        state.publish_results = results
        return state
