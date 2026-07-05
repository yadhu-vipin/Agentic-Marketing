"""
GeminiLLMService — wraps Google Gemini REST API using urllib.
"""

import asyncio
import json
import logging
import time
import urllib.error
import urllib.request

from marketing_agent.configs.settings import get_settings
from marketing_agent.services.llm.base import LLMService

logger = logging.getLogger(__name__)


class GeminiLLMService(LLMService):

    def __init__(self) -> None:
        pass

    def _endpoint(self) -> str:
        settings = get_settings()
        model = settings.gemini_model or settings.ai_model or "gemini-1.5-flash"
        api_key = settings.gemini_api_key or settings.ai_provider_api_key
        return (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={api_key}"
        )

    def _call(self, prompt: str, *, json_mode: bool, temperature: float = 0.2) -> str | None:
        settings = get_settings()
        api_key = settings.gemini_api_key or settings.ai_provider_api_key
        if not api_key:
            logger.warning("[Gemini] API Key not set")
            return None

        generation_config: dict = {"temperature": temperature}
        if json_mode:
            generation_config["responseMimeType"] = "application/json"

        payload = json.dumps(
            {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": generation_config,
            }
        ).encode()

        _MAX_RETRIES = 2
        _BACKOFF_SEC = 3
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                req = urllib.request.Request(
                    self._endpoint(),
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=45) as resp:
                    body = json.loads(resp.read())
                return body["candidates"][0]["content"]["parts"][0]["text"]
            except urllib.error.HTTPError as exc:
                err_body = ""
                try:
                    err_body = exc.read().decode()[:500]
                except Exception:
                    pass
                if exc.code in (429, 500, 503) and attempt < _MAX_RETRIES:
                    wait = _BACKOFF_SEC * attempt
                    logger.warning(
                        f"[Gemini] {exc.code} (attempt {attempt}/{_MAX_RETRIES}) — retrying in {wait}s"
                    )
                    time.sleep(wait)
                    continue
                logger.error(f"[Gemini] call failed: HTTP {exc.code} - {err_body}")
                return None
            except (urllib.error.URLError, KeyError, IndexError, ValueError, TimeoutError) as exc:
                logger.error(f"[Gemini] call failed: {exc}")
                return None
        return None

    async def generate_text(self, prompt: str) -> str:
        res = await asyncio.to_thread(self._call, prompt, json_mode=False)
        return res or ""

    async def generate_json(self, prompt: str) -> dict:
        res = await asyncio.to_thread(self._call, prompt, json_mode=True)
        if not res:
            return {}
        cleaned = (
            res.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        )
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logger.error("[Gemini] response was not valid JSON")
            return {}
