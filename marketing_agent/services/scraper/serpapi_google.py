"""
SerpApiGoogleScraper — discovers leads via SerpApi Google Maps.

Source of truth: legacy/fastapi-leadgen/src/lead_generation/scrapers/serpapi_google.py
Phase 2: port that file's run() logic here verbatim, updating imports only.
"""

import logging

from marketing_agent.configs.settings import get_settings
from marketing_agent.models.lead import Lead
from marketing_agent.models.research import SearchCriteria
from marketing_agent.services.scraper.base import ScraperService

logger = logging.getLogger(__name__)


class SerpApiGoogleScraper(ScraperService):
    name = "serpapi_google"
    label = "Google Maps via SerpApi"

    def __init__(self) -> None:
        self._api_key = get_settings().serpapi_api_key

    async def run(self, criteria: SearchCriteria) -> list[Lead]:
        if not self._api_key:
            logger.warning(
                "[SerpApiGoogleScraper] SERPAPI_API_KEY not set — returning empty list"
            )
            return []
        # TODO (Phase 2): port logic from
        #   legacy/fastapi-leadgen/src/lead_generation/scrapers/serpapi_google.py
        raise NotImplementedError(
            "SerpApiGoogleScraper.run() — Phase 2 port pending. "
            "Use SampleScraper for now."
        )
