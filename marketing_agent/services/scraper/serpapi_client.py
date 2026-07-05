"""
SerpApi Google Search client — paginated fetch with retries and raw logging.
"""

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from marketing_agent.configs.settings import get_settings

_MAX_RETRIES = 3
_BACKOFF_BASE = 2
_PAGE_SIZE = 10

_recent_calls: list[float] = []


def _slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (text or "query").lower()).strip("-")
    return s[:50] or "query"


def _check_rate_limit() -> bool:
    settings = get_settings()
    window = time.time() - 60
    global _recent_calls
    _recent_calls = [t for t in _recent_calls if t > window]
    return len(_recent_calls) < settings.serpapi_rate_limit_per_min


def _record_call() -> None:
    _recent_calls.append(time.time())


def _log_raw(query: str, start: int, data: dict) -> None:
    settings = get_settings()
    if not settings.serpapi_log_raw:
        return
    log_dir = os.path.join(settings.outputs_dir, "serpapi_logs")
    os.makedirs(log_dir, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    path = os.path.join(log_dir, f"{ts}_{_slug(query)}_start{start}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def fetch_page(query: str, start: int = 0) -> dict:
    settings = get_settings()
    if not settings.has_serpapi:
        raise RuntimeError("SERPAPI_API_KEY not configured")

    params = {
        "engine": "google",
        "api_key": settings.serpapi_api_key,
        "q": query,
        "start": str(start),
        "output": "json",
    }
    url = f"{settings.serpapi_base_url}?{urllib.parse.urlencode(params)}"
    last_err = None
    for attempt in range(_MAX_RETRIES):
        if not _check_rate_limit():
            raise RuntimeError(
                f"SerpApi rate limit exceeded ({settings.serpapi_rate_limit_per_min}/min)"
            )
        try:
            req = urllib.request.Request(url, headers={"User-Agent": settings.user_agent})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
            _record_call()
            _log_raw(query, start, data)
            if data.get("error"):
                raise RuntimeError(data["error"])
            return data
        except urllib.error.HTTPError as exc:
            last_err = f"HTTP {exc.code}"
            if exc.code in (429, 500, 502, 503, 504) and attempt < _MAX_RETRIES - 1:
                time.sleep(_BACKOFF_BASE ** attempt)
                continue
            raise RuntimeError(last_err) from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_err = str(exc)
            if attempt < _MAX_RETRIES - 1:
                time.sleep(_BACKOFF_BASE ** attempt)
                continue
            raise RuntimeError(last_err) from exc
    raise RuntimeError(last_err or "SerpApi request failed")


def fetch_all(query: str, max_results: int, *, on_page=None) -> list[dict]:
    settings = get_settings()
    pages: list[dict] = []
    organic_count = 0
    start = 0
    for _ in range(settings.serpapi_max_pages):
        if organic_count >= max_results:
            break
        data = fetch_page(query, start=start)
        pages.append(data)
        organic = data.get("organic_results") or []
        if not isinstance(organic, list) or not organic:
            break
        organic_count += len(organic)
        if on_page:
            on_page(start, len(organic))
        start += _PAGE_SIZE
    return pages
