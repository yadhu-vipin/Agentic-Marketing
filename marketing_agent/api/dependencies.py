"""Shared FastAPI dependencies."""

from functools import lru_cache

from marketing_agent.orchestrator import MarketingOrchestrator


@lru_cache
def get_orchestrator() -> MarketingOrchestrator:
    """Singleton orchestrator injected into route handlers."""
    return MarketingOrchestrator()
