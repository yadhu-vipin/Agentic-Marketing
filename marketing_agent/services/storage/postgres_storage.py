"""PostgresStorageService — concrete PostgreSQL storage service."""

import asyncio
import logging
from typing import Any, Optional

from sqlalchemy import create_engine, Column, String, JSON, DateTime, func
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from marketing_agent.configs.settings import get_settings
from marketing_agent.services.storage.base import StorageService

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


class CampaignStateModel(Base):
    __tablename__ = "campaign_states"

    key = Column(String(255), primary_key=True)
    data = Column(JSON, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


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


class PostgresStorageService(StorageService):
    def __init__(self):
        # Auto-create tables on initialization for dev safety/tests
        try:
            engine = get_engine()
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables verified/created successfully.")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")

    def _sync_save(self, key: str, data: Any) -> None:
        db = get_session()
        try:
            model = db.query(CampaignStateModel).filter(CampaignStateModel.key == key).first()
            if model:
                model.data = data
            else:
                model = CampaignStateModel(key=key, data=data)
                db.add(model)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save key '{key}' to database: {e}")
            raise e
        finally:
            db.close()

    def _sync_load(self, key: str) -> Optional[Any]:
        db = get_session()
        try:
            model = db.query(CampaignStateModel).filter(CampaignStateModel.key == key).first()
            return model.data if model else None
        except Exception as e:
            logger.error(f"Failed to load key '{key}' from database: {e}")
            return None
        finally:
            db.close()

    async def save(self, key: str, data: Any) -> None:
        await asyncio.to_thread(self._sync_save, key, data)

    async def load(self, key: str) -> Any:
        return await asyncio.to_thread(self._sync_load, key)
