"""
GeminiLLMService — wraps google.generativeai.

Source of truth for existing prompt logic:
    legacy/fastapi-leadgen/src/shared/gemini.py

Phase 2: move that file's call logic into generate_text() / generate_json() here.
"""

import json
import logging

from marketing_agent.configs.settings import get_settings
from marketing_agent.services.llm.base import LLMService

logger = logging.getLogger(__name__)


class GeminiLLMService(LLMService):

    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.ai_provider_api_key
        self._model_name = settings.ai_model
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import google.generativeai as genai  # type: ignore
                genai.configure(api_key=self._api_key)
                self._client = genai.GenerativeModel(self._model_name)
            except ImportError:
                raise RuntimeError(
                    "google-generativeai is not installed. "
                    "Run: pip install google-generativeai"
                )
        return self._client

    async def generate_text(self, prompt: str) -> str:
        # TODO (Phase 2): port async streaming from legacy/shared/gemini.py
        import asyncio
        client = self._get_client()
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, lambda: client.generate_content(prompt)
        )
        return response.text

    async def generate_json(self, prompt: str) -> dict:
        json_prompt = (
            f"{prompt}\n\nRespond ONLY with valid JSON. No markdown, no explanation."
        )
        raw = await self.generate_text(json_prompt)
        # Strip markdown fences if the model adds them
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            logger.error("GeminiLLMService: failed to parse JSON response: %s", exc)
            return {}
