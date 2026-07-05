"""
Convert raw scraper dicts into unified Lead objects and remove duplicates.
Dedup matches on (in order): phone, website domain, name+address prefix.
"""

import re
from urllib.parse import urlparse

from marketing_agent.models.lead import Lead
from marketing_agent.core.utils.phone import clean_phone


def _normalize_rating(value) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    match = re.search(r"\d+(\.\d+)?", str(value))
    return float(match.group()) if match else None


def _normalize_website(website: str | None) -> str | None:
    if not website:
        return None
    website = website.strip()
    if not website:
        return None
    if not website.startswith(("http://", "https://")):
        website = "http://" + website.lstrip("/")
    return website


def to_lead(raw: dict, source: str | None = None) -> Lead | None:
    """Map a raw scraper dict to a normalized Lead. Returns None if unusable."""
    name = (raw.get("name") or "").strip()
    if not name:
        return None
    return Lead(
        name=name,
        category=raw.get("category") or raw.get("business_type"),
        address=raw.get("address"),
        phone=clean_phone(raw.get("phone")),
        email=raw.get("email"),
        website=_normalize_website(raw.get("website")),
        rating=_normalize_rating(raw.get("rating")),
        reviews=raw.get("reviews"),
        source=source or raw.get("source", "unknown"),
        metadata={
            k: v
            for k, v in raw.items()
            if k not in {
                "name", "category", "business_type", "address", "phone",
                "email", "website", "rating", "reviews", "source",
            }
            and v is not None
        },
    )


def _key(s: str | None) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def _domain(url: str | None) -> str | None:
    if not url or "justdial.com" in url or "indiamart.com" in url:
        return None
    try:
        netloc = urlparse(url).netloc or urlparse(url).path
        return netloc[4:].lower() if netloc.startswith("www.") else netloc.lower()
    except ValueError:
        return None


def deduplicate(leads: list[Lead]) -> list[Lead]:
    unique: list[Lead] = []
    by_phone: dict[str, int] = {}
    by_domain: dict[str, int] = {}
    by_name: dict[str, int] = {}

    for lead in leads:
        idx = None
        phone_digits = re.sub(r"\D", "", lead.phone or "")
        if len(phone_digits) >= 7 and phone_digits in by_phone:
            idx = by_phone[phone_digits]

        domain = _domain(lead.website)
        if idx is None and domain and domain in by_domain:
            idx = by_domain[domain]

        name_key = f"{_key(lead.name)}|{_key(lead.address)[:15]}"
        if idx is None and _key(lead.name) and name_key in by_name:
            idx = by_name[name_key]

        if idx is not None:
            existing = unique[idx]
            for fld in ("category", "address", "phone", "email", "website", "rating", "reviews"):
                if not getattr(existing, fld) and getattr(lead, fld):
                    setattr(existing, fld, getattr(lead, fld))
            sources = {existing.source, lead.source}
            existing.source = ", ".join(sorted(s for s in sources if s))
            continue

        new_idx = len(unique)
        unique.append(lead)
        if len(phone_digits) >= 7:
            by_phone[phone_digits] = new_idx
        if domain:
            by_domain[domain] = new_idx
        if _key(lead.name):
            by_name[name_key] = new_idx

    return unique
