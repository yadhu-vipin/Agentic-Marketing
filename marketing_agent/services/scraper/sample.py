"""
SampleScraper — returns canned fixtures for demo / offline testing.
"""

from marketing_agent.models.lead import Lead
from marketing_agent.models.research import SearchCriteria
from marketing_agent.services.scraper.base import BaseScraper, register_scraper

_SAMPLE: list[dict] = [
    {
        "name": "Toit Brewpub",
        "category": "restaurant",
        "address": "298, 100 Feet Rd, Indiranagar, Bengaluru",
        "phone": "080 4091 4444",
        "website": "https://toit.in",
        "rating": 4.4,
        "source": "sample",
    },
    {
        "name": "Casa Fresco Cafe",
        "category": "cafe",
        "address": "12th Main, Indiranagar, Bengaluru",
        "phone": None,
        "website": None,
        "rating": 4.2,
        "source": "sample",
    },
]


@register_scraper
class SampleScraper(BaseScraper):
    name = "sample"
    label = "Sample (demo data)"

    async def run(self, criteria: SearchCriteria) -> list[Lead]:
        self.emit("Starting sample scraper...")
        limit = criteria.max_results_per_target
        leads = [Lead(**d) for d in _SAMPLE[:limit]]
        self.emit(f"Found {len(leads)} sample leads.")
        return leads
