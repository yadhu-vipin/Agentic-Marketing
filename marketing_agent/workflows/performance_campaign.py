"""
PerformanceCampaignWorkflow — Full funnel with analytics.

Steps:  ResearchCapability → PlanningCapability → ContentCapability
        → PublishingCapability → AnalyticsCapability
Input:  product_name, product_description, platforms, target_audience, location
Output: state.assets, state.publish_results, state.analytics (placeholder)

Note: AnalyticsCapability is a placeholder until Meta Insights is integrated.
"""

from marketing_agent.capabilities.analytics import AnalyticsCapability
from marketing_agent.capabilities.content import ContentCapability
from marketing_agent.capabilities.planning import PlanningCapability
from marketing_agent.capabilities.publishing import PublishingCapability
from marketing_agent.capabilities.research import ResearchCapability
from marketing_agent.services.llm.gemini import GeminiLLMService
from marketing_agent.services.publishing.meta_facebook import MetaFacebookPublisher
from marketing_agent.services.publishing.meta_instagram import MetaInstagramPublisher
from marketing_agent.services.scraper.sample import SampleScraper
from marketing_agent.workflows.base import Workflow


class PerformanceCampaignWorkflow(Workflow):
    name = "performance_campaign"

    def __init__(self) -> None:
        super().__init__()
        llm = GeminiLLMService()
        publishers = {
            "facebook": MetaFacebookPublisher(),
            "instagram": MetaInstagramPublisher(),
        }
        self.capabilities = [
            ResearchCapability(SampleScraper(), llm),
            PlanningCapability(llm),
            ContentCapability(llm),
            PublishingCapability(publishers),
            AnalyticsCapability(),
        ]
