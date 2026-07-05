"""
LLM-assisted website classification and directory/listicle extraction.

Distinguishes single-business sites from directories, then extracts individual
businesses from aggregator pages when needed.
"""

import json
import re
import time
import urllib.error
import urllib.request

from marketing_agent.configs.settings import get_settings

_CLASSIFY_PROMPT = """Classify this web page for B2B lead generation.

URL: {url}
Page title: {title}
Text sample:
{text}

Return JSON only:
{{"site_type": "single_business|directory|listicle|unknown",
  "confidence": "high|medium|low",
  "reason": "<one sentence>",
  "business_name": "<if single_business, the company name else null>"}}"""

_EXTRACT_PROMPT = """This page lists multiple businesses (directory or listicle).
Extract individual businesses that could be sales leads.

URL: {url}
Text sample:
{text}

Return JSON array only (max 15 entries):
[{{"name": "<business name>", "website": "<url or null>", "phone": "<or null>",
  "email": "<or null>", "address": "<or null>", "category": "<or null>"}}]

Skip navigation links, ads, and the directory site itself. Prefer entries with contact info."""

_SUMMARY_PROMPT = """Summarize this business from its website text for sales outreach.

Business: {name}
URL: {url}
Text:
{text}

Return JSON only:
{{"summary": "<2 sentences on what they do>", "services": ["..."], "tone": "<formal/casual/premium/etc>"}}"""

_DIRECTORY_HOSTS = (
    "justdial.com",
    "indiamart.com",
    "sulekha.com",
    "yellowpages",
    "tripadvisor",
    "zomato.com",
    "swiggy.com",
    "magicpin",
    "urbancompany.com",
    "foursquare.com",
)


def _endpoint() -> str:
    settings = get_settings()
    model = settings.gemini_model or settings.ai_model
    api_key = settings.gemini_api_key or settings.ai_provider_api_key
    return (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )


def _call(prompt: str, *, json_mode: bool, temperature: float) -> str | None:
    settings = get_settings()
    api_key = settings.gemini_api_key or settings.ai_provider_api_key
    if not api_key:
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
                _endpoint(),
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
                print(
                    f"[Gemini] {exc.code} (attempt {attempt}/{_MAX_RETRIES}) — retrying in {wait}s — {err_body}"
                )
                time.sleep(wait)
                continue
            print(f"[Gemini] call failed: HTTP {exc.code} — {err_body}")
            return None
        except (urllib.error.URLError, KeyError, IndexError, ValueError, TimeoutError) as exc:
            print(f"[Gemini] call failed: {exc}")
            return None
    return None


def generate_json(prompt: str, *, temperature: float = 0.2) -> dict | list | None:
    text = _call(prompt, json_mode=True, temperature=temperature)
    if not text:
        return None
    cleaned = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        print("[Gemini] response was not valid JSON")
        return None


def _strip_html(html: str, limit: int = 8000) -> str:
    text = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.I | re.S)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def _title_from_html(html: str) -> str:
    m = re.search(r"<title[^>]*>([^<]+)</title>", html, re.I)
    return m.group(1).strip() if m else ""


def _heuristic_type(url: str, html: str) -> str | None:
    host = (url or "").lower()
    if any(h in host for h in _DIRECTORY_HOSTS):
        return "directory"
    text = _strip_html(html, 3000).lower()
    listicle_signals = ("top 10", "top 15", "best ", "list of", "directory", "near me", "in ")
    if sum(1 for s in listicle_signals if s in text) >= 2:
        return "listicle"
    return None


def classify_site(html: str, url: str) -> dict:
    hint = _heuristic_type(url, html)
    if hint:
        pass  # still try LLM but keep hint as fallback

    text = _strip_html(html)
    title = _title_from_html(html)
    result = generate_json(
        _CLASSIFY_PROMPT.format(url=url, title=title[:200], text=text[:6000]),
        temperature=0.2,
    )
    if isinstance(result, dict) and result.get("site_type"):
        if hint and result.get("site_type") == "unknown":
            result["site_type"] = hint
        return result
    return {
        "site_type": hint or "unknown",
        "confidence": "low",
        "reason": "Could not classify",
        "business_name": None,
    }


def extract_directory_leads(html: str, url: str) -> list[dict]:
    text = _strip_html(html, 12000)
    result = generate_json(
        _EXTRACT_PROMPT.format(url=url, text=text),
        temperature=0.3,
    )
    if not isinstance(result, list):
        return []
    rows = []
    for item in result[:15]:
        if not isinstance(item, dict):
            continue
        name = (item.get("name") or "").strip()
        if not name or len(name) < 2:
            continue
        rows.append(
            {
                "name": name,
                "website": item.get("website"),
                "phone": item.get("phone"),
                "email": item.get("email"),
                "address": item.get("address"),
                "category": item.get("category"),
                "metadata": {
                    "extracted_from_directory": url,
                    "site_type": "directory_entry",
                },
            }
        )
    return rows


def summarize_business(html: str, url: str, name: str) -> dict:
    text = _strip_html(html, 10000)
    result = generate_json(
        _SUMMARY_PROMPT.format(name=name, url=url, text=text[:8000]),
        temperature=0.4,
    )
    return result if isinstance(result, dict) else {}
