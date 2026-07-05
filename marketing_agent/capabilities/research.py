"""ResearchCapability — discovers leads and summarises them."""

import asyncio
import logging

from marketing_agent.capabilities.base import Capability
from marketing_agent.configs.settings import get_settings
from marketing_agent.core.utils.normalize import deduplicate
from marketing_agent.models.lead import Lead
from marketing_agent.services.llm import extract_criteria
from marketing_agent.services.llm.base import LLMService
from marketing_agent.services.llm.gemini import GeminiLLMService
from marketing_agent.services.scraper import get_scraper
from marketing_agent.state import CampaignState

logger = logging.getLogger(__name__)


class ResearchCapability(Capability):
    name = "research"

    def __init__(self, scraper=None, llm: LLMService | None = None) -> None:
        self._scraper = scraper
        self._llm = llm or GeminiLLMService()

    async def _execute(self, state: CampaignState) -> CampaignState:
        # 1. Extract SearchCriteria from brief
        brief = state.product_description or state.product_name
        state.add_log("Extracting search intent from brief...")
        criteria = extract_criteria(brief)

        # Sync back targets & location to state
        if criteria.targets:
            state.target_audience = ", ".join(criteria.targets)
        if criteria.location:
            state.location = criteria.location

        # 2. Determine which scraper IDs to run
        settings = get_settings()
        scraper_ids = state.scrapers
        if not scraper_ids:
            scraper_ids = ["serpapi_google"] if settings.has_serpapi else ["google_maps"]

        state.add_log(f"Selected scrapers: {scraper_ids}")

        # 3. Instantiate and run selected scrapers concurrently
        scrapers = [s for s in (get_scraper(sid) for sid in scraper_ids) if s]
        if not scrapers:
            state.add_log("No valid scrapers found.")
            state.leads = []
            return state

        def progress(stage, message):
            state.add_log(f"[{stage}] {message}")

        for s in scrapers:
            s.on_progress = progress

        state.add_log(
            f"Scraping {len(scraper_ids)} source(s) for {len(criteria.search_terms())} target(s)..."
        )
        results = await asyncio.gather(
            *(s.run(criteria) for s in scrapers), return_exceptions=True
        )

        collected: list[Lead] = []
        for s, res in zip(scrapers, results):
            if isinstance(res, (Exception, BaseException)):
                msg = f"[pipeline] {s.name} error: {res}"
                state.add_log(msg)
                logger.error(msg)
            elif isinstance(res, list):
                collected.extend(res)

        # 4. Deduplicate collected leads
        state.leads = deduplicate(collected)
        state.add_log(f"Collected {len(state.leads)} unique leads after dedupe.")

        # 5. Summarize leads
        if state.leads:
            names = [lead.name for lead in state.leads[:5]]
            prompt = (
                f"Summarise these {len(state.leads)} leads in 2 sentences "
                f"for a campaign targeting '{state.target_audience}': {names}"
            )
            state.research_summary = await self._llm.generate_text(prompt)

        return state
