"""
Fetch B2B websites and extract contact details from HTML.

Visits the landing URL plus likely contact/about pages when email or phone
is missing on the homepage.
"""

import asyncio
import html as html_lib
import json
import re
import urllib.error
import urllib.parse
import urllib.request

from marketing_agent.configs.settings import get_settings
from marketing_agent.core.utils.phone import clean_phone
from marketing_agent.services.scraper import site_analyzer

_MAX_BYTES = 750_000
_MAX_PAGES_SINGLE = 6
_MAX_PAGES_QUICK = 4

_CONTACT_PATHS = (
    "/contact",
    "/contact-us",
    "/contact_us",
    "/contactus",
    "/about",
    "/about-us",
    "/about_us",
    "/get-in-touch",
    "/reach-us",
    "/en/contact",
    "/contact.html",
    "/about.html",
    "/about.html",
)

_DEEP_PATHS = (
    "/team",
    "/our-team",
    "/menu",
    "/services",
    "/products",
    "/locations",
    "/store-locator",
)

_JUNK_EMAIL_EXACT = {
    "example.com",
    "example.org",
    "example.net",
    "domain.com",
    "email.com",
    "yourdomain.com",
}

_JUNK_EMAIL_SUFFIX = {
    "sentry.io",
    "wixpress.com",
    "facebook.com",
    "instagram.com",
    "google.com",
    "youtube.com",
    "twitter.com",
    "linkedin.com",
    "schema.org",
    "w3.org",
}

_EMAIL_RE = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    re.I,
)
_OBFUSCATED_EMAIL_RE = re.compile(
    r"([a-zA-Z0-9._%+\-]+)\s*(?:@|\[at\]|\(at\)|\s+at\s+)\s*"
    r"([a-zA-Z0-9.\-]+)\s*(?:\.|\[dot\]|\(dot\)|\s+dot\s+)\s*([a-zA-Z]{2,})",
    re.I,
)
_CONTACT_HREF_RE = re.compile(
    r"""href=["']([^"']*(?:contact|about|reach|connect|enquiry|inquiry)[^"']*)["']""",
    re.I,
)
_JSON_LD_RE = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.I | re.S,
)
_CFEMAIL_RE = re.compile(r'data-cfemail=["\']([a-f0-9]+)["\']', re.I)
_TEL_RE = re.compile(r"tel:([+\d\s\-().]+)", re.I)
_ADDRESS_RE = re.compile(
    r"(?:address|location|office)[^<]{0,40}</[^>]+>\s*([^<]{15,120})",
    re.I,
)
_PIN_ADDRESS_RE = re.compile(
    r"[A-Za-z0-9\s,.\-/]{10,80}\b\d{6}\b(?:\s*,?\s*India)?",
    re.I,
)


def _fetch_html(url: str) -> str:
    settings = get_settings()
    req = urllib.request.Request(url, headers={"User-Agent": settings.user_agent})
    with urllib.request.urlopen(req, timeout=settings.serpapi_website_timeout) as resp:
        raw = resp.read(_MAX_BYTES)
        ctype = resp.headers.get("Content-Type", "").lower()
        if raw and (
            "html" in ctype or "text" in ctype or "<" in raw[:200].decode(errors="ignore")
        ):
            return raw.decode(errors="replace")
        return ""


def _base_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def _resolve_url(base: str, href: str) -> str | None:
    href = html_lib.unescape(href.strip())
    if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
        return None
    return urllib.parse.urljoin(base, href)


def _same_site(url: str, root: str) -> bool:
    try:
        return (
            urllib.parse.urlparse(url).netloc.lower() == urllib.parse.urlparse(root).netloc.lower()
        )
    except ValueError:
        return False


def _decode_cfemail(encoded: str) -> str | None:
    try:
        key = int(encoded[:2], 16)
        chars = [chr(int(encoded[i : i + 2], 16) ^ key) for i in range(2, len(encoded), 2)]
        email = "".join(chars)
        return email if "@" in email else None
    except (ValueError, IndexError):
        return None


def _walk_json_ld(node) -> dict[str, str]:
    found: dict[str, str] = {}
    if isinstance(node, list):
        for item in node:
            found.update(_walk_json_ld(item))
        return found
    if not isinstance(node, dict):
        return found

    email = node.get("email")
    if isinstance(email, str) and "@" in email:
        found.setdefault("email", email.strip())
    elif isinstance(email, dict) and email.get("@type") == "ContactPoint":
        val = email.get("email")
        if isinstance(val, str):
            found.setdefault("email", val.strip())

    phone = node.get("telephone") or node.get("phone")
    if isinstance(phone, str):
        found.setdefault("phone", phone.strip())

    address = node.get("address")
    if isinstance(address, str):
        found.setdefault("address", address.strip())
    elif isinstance(address, dict):
        parts = [
            address.get("streetAddress"),
            address.get("addressLocality"),
            address.get("addressRegion"),
            address.get("postalCode"),
        ]
        line = ", ".join(p.strip() for p in parts if isinstance(p, str) and p.strip())
        if line:
            found.setdefault("address", line)

    for key in ("@graph", "department", "subOrganization", "location", "contactPoint"):
        child = node.get(key)
        if child is not None:
            found.update(_walk_json_ld(child))
    return found


def _extract_json_ld(html: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for match in _JSON_LD_RE.finditer(html):
        try:
            data = json.loads(match.group(1))
        except (json.JSONDecodeError, ValueError):
            continue
        out.update(_walk_json_ld(data))
    return out


def _email_domain(email: str) -> str:
    return email.split("@", 1)[-1].lower()


def _is_junk_email(email: str) -> bool:
    email = email.lower().strip()
    if not email or "@" not in email:
        return True
    local, domain = email.split("@", 1)
    if domain in _JUNK_EMAIL_EXACT:
        return True
    if any(domain == d or domain.endswith("." + d) for d in _JUNK_EMAIL_SUFFIX):
        return True
    if local in {"noreply", "no-reply", "donotreply", "mailer-daemon", "postmaster"}:
        return True
    if re.search(r"\.(png|jpg|jpeg|gif|svg|webp)$", domain):
        return True
    return False


def _score_email(email: str, site_domain: str | None) -> int:
    if _is_junk_email(email):
        return -100
    score = 0
    local, domain = email.lower().split("@", 1)
    if site_domain and (domain == site_domain or domain.endswith("." + site_domain)):
        score += 20
    if local in {"contact", "info", "hello", "sales", "support", "enquiry", "inquiries", "mail"}:
        score += 8
    if local.startswith("noreply") or local.startswith("no-reply"):
        score -= 20
    return score


def _collect_emails(html: str, site_domain: str | None) -> list[str]:
    text = html_lib.unescape(html)
    candidates: list[str] = []

    for match in _EMAIL_RE.finditer(text):
        candidates.append(match.group(0))

    for match in _OBFUSCATED_EMAIL_RE.finditer(text):
        candidates.append(f"{match.group(1)}@{match.group(2)}.{match.group(3)}")

    for match in _CFEMAIL_RE.finditer(text):
        decoded = _decode_cfemail(match.group(1))
        if decoded:
            candidates.append(decoded)

    for match in re.finditer(
        r'mailto:([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})', text, re.I
    ):
        candidates.append(match.group(1))

    scored = sorted(
        {c.strip().rstrip(".,;") for c in candidates if c},
        key=lambda e: _score_email(e, site_domain),
        reverse=True,
    )
    return [e for e in scored if _score_email(e, site_domain) > 0]


def _extract_email(html: str, site_domain: str | None = None) -> str | None:
    structured = _extract_json_ld(html)
    if structured.get("email") and not _is_junk_email(structured["email"]):
        return structured["email"]

    emails = _collect_emails(html, site_domain)
    return emails[0] if emails else None


def _extract_phone(html: str) -> str | None:
    structured = _extract_json_ld(html)
    if structured.get("phone"):
        cleaned = clean_phone(structured["phone"])
        if cleaned:
            return cleaned

    for match in _TEL_RE.finditer(html):
        cleaned = clean_phone(match.group(1))
        if cleaned:
            return cleaned

    for pat in (
        r"\+91[\s\-]?[6-9]\d{4}[\s\-]?\d{5}",
        r"\+91[\s\-]?[6-9]\d{9}",
        r"(?<!\d)[6-9]\d{4}[\s\-]?\d{5}(?!\d)",
    ):
        m = re.search(pat, html)
        if m:
            cleaned = clean_phone(m.group(0))
            if cleaned:
                return cleaned
    return None


def _extract_address(html: str) -> str | None:
    structured = _extract_json_ld(html)
    if structured.get("address"):
        return structured["address"][:200]

    match = _ADDRESS_RE.search(html)
    if match:
        line = re.sub(r"\s+", " ", html_lib.unescape(match.group(1))).strip()
        if len(line) >= 10:
            return line[:200]

    match = _PIN_ADDRESS_RE.search(html_lib.unescape(re.sub(r"<[^>]+>", " ", html)))
    if match:
        return match.group(0).strip()[:200]
    return None


def _extract_title(html: str) -> str | None:
    match = re.search(r"<title[^>]*>([^<]+)</title>", html, re.I)
    return match.group(1).strip() if match else None


def _candidate_urls(
    start_url: str, homepage_html: str, *, max_pages: int = _MAX_PAGES_SINGLE
) -> list[str]:
    base = _base_url(start_url)
    seen = {start_url.rstrip("/")}
    urls: list[str] = [start_url]

    for path in _CONTACT_PATHS + _DEEP_PATHS:
        url = urllib.parse.urljoin(base, path)
        key = url.rstrip("/")
        if key not in seen:
            seen.add(key)
            urls.append(url)

    for href in _CONTACT_HREF_RE.findall(homepage_html):
        resolved_url = _resolve_url(base, href)
        if resolved_url and _same_site(resolved_url, base) and resolved_url.rstrip("/") not in seen:
            seen.add(resolved_url.rstrip("/"))
            urls.append(resolved_url)
        if len(urls) >= max_pages:
            break

    return urls[:max_pages]


def _extract_from_pages(pages: list[tuple[str, str]], site_domain: str | None) -> dict[str, str]:
    found: dict[str, str] = {}
    for url, html in pages:
        if not html:
            continue
        if not found.get("email"):
            email = _extract_email(html, site_domain)
            if email:
                found["email"] = email
                found["email_source"] = url
        if not found.get("phone"):
            phone = _extract_phone(html)
            if phone:
                found["phone"] = phone
                found["phone_source"] = url
        if not found.get("address"):
            address = _extract_address(html)
            if address:
                found["address"] = address
                found["address_source"] = url
        if found.get("email") and found.get("phone"):
            break
    return found


def _merge_enrichment(
    row: dict,
    pages: list[tuple[str, str]],
    site_domain: str | None,
    *,
    site_meta: dict | None = None,
) -> dict:
    extracted = _extract_from_pages(pages, site_domain)
    merged = dict(row)
    if not merged.get("email") and extracted.get("email"):
        merged["email"] = extracted["email"]
    if not merged.get("phone") and extracted.get("phone"):
        merged["phone"] = extracted["phone"]
    if not merged.get("address") and extracted.get("address"):
        merged["address"] = extracted["address"]
    if not merged.get("name") or merged["name"] == merged.get("website"):
        for _, html in pages:
            title = _extract_title(html)
            if title:
                merged["name"] = re.sub(r"\s*[|\-/].*$", "", title).strip()[:120]
                break

    meta = dict(merged.get("metadata") or {})
    meta["website_enriched"] = True
    meta["pages_fetched"] = len(pages)
    if extracted.get("email_source"):
        meta["email_source"] = extracted["email_source"]
    if site_meta:
        meta.update(site_meta)
    merged["metadata"] = meta
    return merged


def _enrich_single(row: dict, *, deep: bool = True) -> dict:
    url = row.get("website")
    if not url:
        return row

    site_domain = urllib.parse.urlparse(url).netloc.lower()
    if site_domain.startswith("www."):
        site_domain = site_domain[4:]

    max_pages = _MAX_PAGES_SINGLE if deep else _MAX_PAGES_QUICK
    pages: list[tuple[str, str]] = []
    try:
        homepage = _fetch_html(url)
        pages.append((url, homepage))
        for extra_url in _candidate_urls(url, homepage, max_pages=max_pages)[1:]:
            try:
                pages.append((extra_url, _fetch_html(extra_url)))
            except (urllib.error.URLError, TimeoutError, ValueError, OSError):
                continue
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        return row

    site_meta = {}
    if deep and pages:
        summary = site_analyzer.summarize_business(pages[0][1], url, row.get("name") or "")
        if summary.get("summary"):
            site_meta["site_summary"] = summary.get("summary")
        if summary.get("services"):
            site_meta["site_services"] = summary.get("services")
        if summary.get("tone"):
            site_meta["site_tone"] = summary.get("tone")

    return _merge_enrichment(row, pages, site_domain, site_meta=site_meta)


def enrich_row(row: dict) -> dict:
    return _enrich_single(row, deep=True)


def enrich_expand(row: dict) -> list[dict]:
    """Classify site; expand directories into multiple leads or deep-enrich clients."""
    url = row.get("website")
    if not url:
        return [row]

    try:
        homepage = _fetch_html(url)
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        return [row]

    classification = site_analyzer.classify_site(homepage, url)
    site_type = classification.get("site_type", "unknown")

    if site_type in ("directory", "listicle"):
        extracted = site_analyzer.extract_directory_leads(homepage, url)
        if not extracted:
            meta = dict(row.get("metadata") or {})
            meta["site_type"] = site_type
            meta["classification"] = classification
            return [_merge_enrichment({**row, "metadata": meta}, [(url, homepage)], None)]

        out: list[dict] = []
        for entry in extracted:
            entry_meta = dict(entry.get("metadata") or {})
            entry_meta["classification"] = classification
            entry["metadata"] = entry_meta
            if entry.get("website"):
                out.append(_enrich_single(entry, deep=False))
            else:
                merged = dict(row)
                merged.update({k: v for k, v in entry.items() if v and k != "metadata"})
                merged["metadata"] = {**dict(row.get("metadata") or {}), **entry_meta}
                out.append(merged)
        return out or [row]

    merged = _enrich_single(
        {
            **row,
            "metadata": {
                **(row.get("metadata") or {}),
                "site_type": site_type,
                "classification": classification,
            },
        },
        deep=True,
    )
    if classification.get("business_name") and merged.get("name") == url:
        merged["name"] = classification["business_name"]
    return [merged]


async def enrich_all(candidates: list[dict], *, on_progress=None) -> list[dict]:
    settings = get_settings()
    sem = asyncio.Semaphore(settings.serpapi_website_concurrency)
    total = len(candidates)

    async def one(i: int, row: dict) -> list[dict]:
        async with sem:
            if on_progress:
                on_progress(i + 1, total, row.get("website", ""))
            return await asyncio.to_thread(enrich_expand, row)

    batches = await asyncio.gather(*(one(i, r) for i, r in enumerate(candidates)))
    return [row for batch in batches for row in batch]
