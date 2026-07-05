"""FastAPI application factory."""

from fastapi import FastAPI

from marketing_agent.api.routes import campaigns, health, leads, workflows
from marketing_agent.configs.settings import get_settings
from marketing_agent.core.logging import configure_logging


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title="Agentic Marketing API",
        version="0.1.0",
        description="Workflow-based AI marketing agency backend.",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    app.include_router(health.router)
    app.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
    app.include_router(leads.router, prefix="/leads", tags=["leads"])
    app.include_router(workflows.router, prefix="/workflows", tags=["workflows"])

    return app


app = create_app()
