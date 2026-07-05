"""GET /health — liveness check."""

import asyncio
import logging
import time
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from marketing_agent.services.storage.postgres_storage import get_engine

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    version: str


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", version="0.1.0")


@router.get("/health/db")
async def health_db() -> JSONResponse:
    """Check database connectivity and measure latency."""
    start_time = time.perf_counter()
    try:
        engine = get_engine()

        def check_conn():
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))

        # Run connection check in a threadpool to keep FastAPI async event loop non-blocking
        await asyncio.to_thread(check_conn)

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.info(f"Database health check: SUCCESS (latency: {latency_ms} ms)")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "ok",
                "database": "connected",
                "provider": "postgres",
                "latency_ms": latency_ms
            }
        )
    except (OperationalError, SQLAlchemyError) as e:
        error_msg = str(e)
        logger.error(f"Database health check: FAILED (SQLAlchemy/OperationalError): {error_msg}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "error",
                "database": "unreachable",
                "error": error_msg
            }
        )
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Database health check: FAILED (Unexpected error): {error_msg}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "error",
                "database": "unreachable",
                "error": error_msg
            }
        )

