"""
Settings — single source of truth for all configurable values.
Reads from .env file and environment variables.
No hardcoded secrets, paths, or URLs anywhere in the codebase.
"""

from pydantic import Field
import os
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
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

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
    scraper_headless: bool = False  # Set to False to watch scraping in a visible browser window
    max_results_per_target: int = 5

    # ── Database ─────────────────────────────────────────────────────────────────
    database_url: str = Field(default="postgresql://postgres:postgres@localhost:5432/agentic_marketing")
    # ── Redis ────────────────────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── App ──────────────────────────────────────────────────────────────────────
    debug: bool = False
    log_level: str = "INFO"
    app_url: str = "http://localhost:8000"

    # ── B2B and email service configuration ───────────────────────────────────────
    outputs_dir: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "outputs",
    )

    # SMTP
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_use_tls: bool = True
    email_max_per_hour: int = 20

    # CRM & tracking
    crm_webhook_url: str = ""
    public_base_url: str = "http://localhost:8000"

    # A/B testing
    ab_min_sends: int = 10

    # Stub modes
    whatsapp_stub_mode: bool = True
    meta_stub_mode: bool = True

    # SerpApi / Scrapers
    serpapi_base_url: str = "https://serpapi.com/search"
    serpapi_rate_limit_per_min: int = 30
    serpapi_max_pages: int = 5
    serpapi_log_raw: bool = True
    serpapi_website_timeout: int = 15
    serpapi_website_concurrency: int = 5
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    # Pollinations
    pollinations_base_url: str = "https://image.pollinations.ai/prompt"
    pollinations_model: str = "flux"
    pollinations_width: int = 1024
    pollinations_height: int = 1024
    pollinations_timeout: int = 120

    @property
    def has_gemini(self) -> bool:
        return bool(self.gemini_api_key or self.ai_provider_api_key)

    @property
    def has_smtp(self) -> bool:
        return bool(self.smtp_host)

    @property
    def has_serpapi(self) -> bool:
        return bool(self.serpapi_api_key)


@lru_cache
def get_settings() -> Settings:
    # Ensure directories are created on initialization
    settings = Settings()
    os.makedirs(settings.outputs_dir, exist_ok=True)
    os.makedirs(os.path.join(settings.outputs_dir, "serpapi_logs"), exist_ok=True)
    return settings

