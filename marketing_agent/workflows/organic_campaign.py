"""
OrganicCampaignWorkflow — Plan → Generate content → Publish to Meta.

Steps:  PlanningCapability → ContentCapability → PublishingCapability
Input:  product_name, product_description, platforms
Output: state.assets (generated), state.publish_results
"""

from marketing_agent.capabilities.content import ContentCapability
from marketing_agent.capabilities.planning import PlanningCapability
from marketing_agent.capabilities.publishing import PublishingCapability
from marketing_agent.services.llm.gemini import GeminiLLMService
from marketing_agent.services.publishing.meta_facebook import MetaFacebookPublisher
from marketing_agent.services.publishing.meta_instagram import MetaInstagramPublisher
from marketing_agent.workflows.base import Workflow


class OrganicCampaignWorkflow(Workflow):
    name = "organic_campaign"

    def __init__(self) -> None:
        super().__init__()
        llm = GeminiLLMService()
        publishers = {
            "facebook": MetaFacebookPublisher(),
            "instagram": MetaInstagramPublisher(),
        }
        self.capabilities = [
            PlanningCapability(llm),
            ContentCapability(llm),
            PublishingCapability(publishers),
        ]
