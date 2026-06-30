"""
LeadGenerationWorkflow — Discover leads → Score → Draft outreach.

Steps:  ResearchCapability → ScoringCapability → OutreachCapability
Input:  product_description, target_audience, location
Output: state.leads (with scores and message drafts)
"""

from marketing_agent.capabilities.outreach import OutreachCapability
from marketing_agent.capabilities.research import ResearchCapability
from marketing_agent.capabilities.scoring import ScoringCapability
from marketing_agent.services.llm.gemini import GeminiLLMService
from marketing_agent.services.scraper.sample import SampleScraper
from marketing_agent.workflows.base import Workflow


class LeadGenerationWorkflow(Workflow):
    name = "lead_generation"

    def __init__(self) -> None:
        super().__init__()
        llm = GeminiLLMService()
        # Phase 2: swap SampleScraper for SerpApiGoogleScraper when SERPAPI_API_KEY is set
        self.capabilities = [
            ResearchCapability(SampleScraper(), llm),
            ScoringCapability(llm),
            OutreachCapability(llm),
        ]
