"""ScraperService ABC — no capability imports Playwright or requests directly."""

from abc import ABC, abstractmethod

from marketing_agent.models.lead import Lead
from marketing_agent.models.research import SearchCriteria


class ScraperService(ABC):
    name: str = "scraper"
    label: str = "Scraper"

    @abstractmethod
    async def run(self, criteria: SearchCriteria) -> list[Lead]:
        """Discover and return leads matching the given criteria."""
        ...
