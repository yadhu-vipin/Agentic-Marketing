"""
Defensive SerpApi JSON parser — optional sections handled safely.
"""

from dataclasses import dataclass, field
from urllib.parse import urlparse

SKIP_DOMAINS = {
    "google.com", "google.co.in", "facebook.com", "linkedin.com",
    "youtube.com", "wikipedia.org", "instagram.com", "twitter.com", "x.com",
    "reddit.com", "quora.com", "amazon.in", "amazon.com",
}


def _domain(url: str | None) -> str | None:
    if not url:
        return None
    try:
        host = urlparse(url).netloc.lower()
        if host.startswith("www."):
            host = host[4:]
        return host or None
    except ValueError:
        return None


def _skip_url(url: str | None) -> bool:
    d = _domain(url)
    if not d:
        return True
    return any(d == s or d.endswith("." + s) for s in SKIP_DOMAINS)


def _safe_dict(val) -> dict:
    return val if isinstance(val, dict) else {}


def _safe_list(val) -> list:
    return val if isinstance(val, list) else []


@dataclass
class ParsedSerpResult:
    organic_candidates: list[dict] = field(default_factory=list)
    direct_leads: list[dict] = field(default_factory=list)
    run_metadata: dict = field(default_factory=dict)


def _parse_organic(data: dict) -> list[dict]:
    rows = []
    for item in _safe_list(data.get("organic_results")):
        if not isinstance(item, dict):
            continue
        link = item.get("link") or item.get("url")
        if _skip_url(link):
            continue
        title = (item.get("title") or "").strip()
        if not title:
            continue
        rows.append({
            "name": title,
            "website": link,
            "category": item.get("source") or item.get("type"),
            "metadata": {
                k: v for k, v in {
                    "snippet": item.get("snippet"),
                    "displayed_link": item.get("displayed_link"),
                    "position": item.get("position"),
                    "date": item.get("date"),
                    "sitelinks": item.get("sitelinks"),
                    "serpapi_section": "organic_results",
                }.items() if v is not None
            },
        })
    return rows


def _parse_local(data: dict) -> list[dict]:
    rows = []
    local = data.get("local_results")
    places = []
    if isinstance(local, dict):
        places = _safe_list(local.get("places")) or _safe_list(local.get("local_results"))
    elif isinstance(local, list):
        places = local
    for item in places:
        if not isinstance(item, dict):
            continue
        name = (item.get("title") or item.get("name") or "").strip()
        if not name:
            continue
        rows.append({
            "name": name,
            "phone": item.get("phone"),
            "address": item.get("address"),
            "website": item.get("website") or item.get("links", {}).get("website") if isinstance(item.get("links"), dict) else item.get("website"),
            "rating": item.get("rating"),
            "reviews": item.get("reviews") or item.get("review_count"),
            "metadata": {"serpapi_section": "local_results", "place_id": item.get("place_id")},
        })
    return rows


def _parse_knowledge_graph(data: dict) -> list[dict]:
    kg = _safe_dict(data.get("knowledge_graph"))
    if not kg:
        return []
    name = (kg.get("title") or kg.get("name") or "").strip()
    if not name:
        return []
    return [{
        "name": name,
        "website": kg.get("website") or kg.get("source", {}).get("link") if isinstance(kg.get("source"), dict) else kg.get("website"),
        "phone": kg.get("phone"),
        "address": kg.get("address"),
        "rating": kg.get("rating"),
        "category": kg.get("type"),
        "metadata": {"serpapi_section": "knowledge_graph", "description": kg.get("description")},
    }]


def parse_response(data: dict) -> ParsedSerpResult:
    data = data or {}
    organic = _parse_organic(data)
    direct = _parse_local(data) + _parse_knowledge_graph(data)

    run_metadata = {
        "search_information": _safe_dict(data.get("search_information")),
        "related_questions": _safe_list(data.get("related_questions"))[:5],
        "news_results": _safe_list(data.get("news_results"))[:5],
        "answer_box": _safe_dict(data.get("answer_box")) or None,
        "inline_images_count": len(_safe_list(data.get("inline_images"))),
    }
    return ParsedSerpResult(
        organic_candidates=organic,
        direct_leads=direct,
        run_metadata=run_metadata,
    )


def parse_pages(pages: list[dict]) -> ParsedSerpResult:
    combined = ParsedSerpResult()
    seen_domains: set[str] = set()
    for page in pages:
        parsed = parse_response(page)
        combined.run_metadata.setdefault("pages", []).append(parsed.run_metadata)
        for row in parsed.direct_leads:
            combined.direct_leads.append(row)
        for row in parsed.organic_candidates:
            dom = _domain(row.get("website"))
            if dom and dom in seen_domains:
                continue
            if dom:
                seen_domains.add(dom)
            combined.organic_candidates.append(row)
    return combined


def dedupe_by_domain(candidates: list[dict]) -> list[dict]:
    seen: set[str] = set()
    out = []
    for row in candidates:
        dom = _domain(row.get("website"))
        if dom and dom in seen:
            continue
        if dom:
            seen.add(dom)
        out.append(row)
    return out
