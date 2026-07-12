"""Shared FastAPI dependencies."""

from functools import lru_cache
from typing import Generator
from sqlalchemy.orm import Session

from marketing_agent.orchestrator import MarketingOrchestrator
from marketing_agent.services.storage.postgres_storage import get_session


@lru_cache
def get_orchestrator() -> MarketingOrchestrator:
    """Singleton orchestrator injected into route handlers."""
    return MarketingOrchestrator()


def get_db() -> Generator[Session, None, None]:
    """Database session dependency for routing."""
    db = get_session()
    try:
        yield db
    finally:
        db.close()

