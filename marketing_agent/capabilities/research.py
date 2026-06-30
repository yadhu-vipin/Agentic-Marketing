"""ResearchCapability — discovers leads and summarises them."""

import logging
from marketing_agent.capabilities.base import Capability
from marketing_agent.models.research import SearchCriteria
from marketing_agent.services.llm.base import LLMService
from marketing_agent.services.scraper.base import ScraperService
from marketing_agent.state import CampaignState

logger = logging.getLogger(__name__)


class ResearchCapability(Capability):
    name = "research"

    def __init__(self, scraper: ScraperService, llm: LLMService) -> None:
        self._scraper = scraper
        self._llm = llm

    async def _execute(self, state: CampaignState) -> CampaignState:
        criteria = SearchCriteria(
            product=state.product_description or state.product_name,
            target_types=[state.target_audience or "general"],
            location=state.location or "",
            max_results_per_target=5,
        )
        state.leads = await self._scraper.run(criteria)
        logger.info("[ResearchCapability] found %d leads", len(state.leads))

        if state.leads:
            names = [l.name for l in state.leads[:5]]
            prompt = (
                f"Summarise these {len(state.leads)} leads in 2 sentences "
                f"for a campaign targeting '{state.target_audience}': {names}"
            )
            state.research_summary = await self._llm.generate_text(prompt)

        return state
