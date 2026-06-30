"""
SampleScraper — returns canned fixtures for demo / offline testing.

Source of truth: legacy/fastapi-leadgen/src/lead_generation/scrapers/sample.py
Phase 2: port the _SAMPLE fixture list here.
"""

from marketing_agent.models.lead import Lead
from marketing_agent.models.research import SearchCriteria
from marketing_agent.services.scraper.base import ScraperService

# Phase 2: move full fixture list from legacy/…/scrapers/sample.py
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


class SampleScraper(ScraperService):
    name = "sample"
    label = "Sample (demo data)"

    async def run(self, criteria: SearchCriteria) -> list[Lead]:
        limit = criteria.max_results_per_target
        return [Lead(**d) for d in _SAMPLE[:limit]]
