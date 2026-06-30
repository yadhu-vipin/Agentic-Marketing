"""
Settings — single source of truth for all configurable values.
Reads from .env file and environment variables.
No hardcoded secrets, paths, or URLs anywhere in the codebase.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ── LLM ──────────────────────────────────────────────────────────────────────
    ai_provider: str = "gemini"
    ai_provider_api_key: str = ""
    ai_model: str = "gemini-2.5-flash"

    # ── Image generation ─────────────────────────────────────────────────────────
    creative_provider: str = "pollinations"
    creative_provider_api_key: str = ""

    # ── Meta Graph API ───────────────────────────────────────────────────────────
    meta_graph_version: str = "v21.0"
    meta_access_token: str = ""
    instagram_access_token: str = ""
    meta_page_id: str = ""
    meta_ig_user_id: str = ""

    # ── Supabase ─────────────────────────────────────────────────────────────────
    next_public_supabase_url: str = ""
    next_public_supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_storage_bucket: str = "product-assets"

    # ── Scrapers ─────────────────────────────────────────────────────────────────
    serpapi_api_key: str = ""
    scraper_headless: bool = True
    max_results_per_target: int = 5

    # ── Database ─────────────────────────────────────────────────────────────────
    database_url: str = "postgresql://postgres:postgres@localhost:5432/agentic_marketing"

    # ── Redis ────────────────────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── App ──────────────────────────────────────────────────────────────────────
    debug: bool = False
    log_level: str = "INFO"
    app_url: str = "http://localhost:8000"


@lru_cache
def get_settings() -> Settings:
    return Settings()
