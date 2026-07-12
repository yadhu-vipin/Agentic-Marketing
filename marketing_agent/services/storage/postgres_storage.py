"""PostgresStorageService — concrete PostgreSQL storage service."""

import asyncio
import logging
from typing import Any, Optional

from sqlalchemy import create_engine, Column, String, JSON, DateTime, func
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from marketing_agent.configs.settings import get_settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass



# Global engine and session makers
_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        settings = get_settings()
        db_url = settings.database_url
        # Handle standard Pydantic/Supabase URL scheme
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
        elif db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
        
        logger.info(f"Initializing SQLAlchemy engine with URL (masked): {db_url.split('@')[-1] if '@' in db_url else db_url}")
        _engine = create_engine(
            db_url,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
    return _engine


def get_session():
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionLocal()


