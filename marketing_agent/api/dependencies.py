"""Shared FastAPI dependencies."""

from functools import lru_cache

from marketing_agent.orchestrator import MarketingOrchestrator
from marketing_agent.services.storage.base import StorageService
from marketing_agent.services.storage.postgres_storage import PostgresStorageService


@lru_cache
def get_orchestrator() -> MarketingOrchestrator:
    """Singleton orchestrator injected into route handlers."""
    return MarketingOrchestrator()


@lru_cache
def get_storage() -> StorageService:
    """Singleton storage service injected into route handlers."""
    return PostgresStorageService()
