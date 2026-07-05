"""
Turn a company's free-text brief into structured SearchCriteria via Gemini.

Nothing is hardcoded — the LLM infers product, target business types,
location preference, and desired lead attributes. If Gemini is unavailable
a minimal heuristic keeps the app usable.
"""

import re

from marketing_agent.models.research import SearchCriteria
from marketing_agent.services.scraper.site_analyzer import generate_json

_PROMPT = """You are a B2B lead-generation analyst. Read the company's brief and
extract structured search intent. Infer everything — do not ask questions.

Brief:
\"\"\"{text}\"\"\"

Return JSON only with this exact shape:
{{
  "company_name": "<company name or empty>",
  "what_they_do": "<one short phrase>",
  "product": "<main product/service to sell>",
  "targets": ["<business types to approach, e.g. cafes, restaurants>"],
  "location": "<geographic preference, or empty>",
  "attributes": ["<desired lead qualities, e.g. premium, high traffic, wholesale buyer>"],
  "additional_requirements": "<anything else relevant, or empty>"
}}"""

_CITIES = (
    r"(?:Bengaluru|Bangalore|Mumbai|New Delhi|Delhi|Chennai|Hyderabad|Pune|Kolkata|"
    r"Ahmedabad|Jaipur|Gurugram|Gurgaon|Noida|Kochi|Cochin|Coimbatore|Chandigarh|"
    r"Indore|Surat|Nagpur|Lucknow|Thiruvananthapuram)"
)
# "Indiranagar and Koramangala, Bangalore" / "Bandra, Mumbai" / "HSR Layout, Bangalore"
_LOCATION_RE = re.compile(
    rf"([A-Z][A-Za-z]+(?:\s+(?:Layout|Nagar|Town|Colony|Road|East|West|North|South))?"
    rf"(?:\s+(?:and|&|,)\s+[A-Z][A-Za-z]+(?:\s+(?:Layout|Nagar|Town|Colony|Road))?)*)"
    rf"\s*,?\s+({_CITIES})\b"
)


def _extract_location(text: str) -> str:
    matches = _LOCATION_RE.findall(text)
    if matches:
        # The last "area(s), City" phrase is usually the *target* preference
        # (the seller's own address tends to come first).
        area, city = matches[-1]
        return f"{area.strip()}, {city}"
    city = re.search(_CITIES, text)
    if city:
        return city.group(0)
    if re.search(r"\bnear(by)?\b|\blocal\b", text, re.I):
        return "nearby"
    return ""


def _extract_product(text: str) -> str:
    m = re.search(
        r"\b(?:specialize in|sell|supply|produce|make|offer[s]?|provide[s]?)\s+([a-z]["
        r"\w\s-]{2,50}?)(?:\s+(?:and|to|for|with|that|in)\b|[.,])",
        text,
        re.I,
    )
    return m.group(1).strip() if m else ""


def _heuristic(text: str) -> SearchCriteria:
    targets: list[str] = []
    for word in (
        "cafe",
        "cafes",
        "restaurant",
        "restaurants",
        "hotel",
        "hotels",
        "bakery",
        "bakeries",
        "gym",
        "gyms",
        "fitness studio",
        "boutique",
        "boutiques",
        "clinic",
        "clinics",
        "office",
        "offices",
        "school",
        "schools",
        "coaching center",
        "coaching centers",
        "store",
        "stores",
        "startup",
        "startups",
        "lifestyle store",
    ):
        if re.search(rf"\b{word}\b", text, re.I):
            base = word.rstrip("s")
            if base not in targets:
                targets.append(base)
    name_match = re.search(
        r"\b(?:i am|we are|this is)\s+([A-Z][\w&' ]{2,40}?)(?:[.,]|\s+(?:is|makes|"
        r"produces|offers|specializes|based|in|a))",
        text,
    )
    return SearchCriteria(
        raw_text=text,
        company_name=name_match.group(1).strip() if name_match else "",
        targets=targets or ["cafe", "restaurant"],
        location=_extract_location(text),
        product=_extract_product(text),
    )


def extract_criteria(text: str, *, max_results_per_target: int = 5) -> SearchCriteria:
    text = (text or "").strip()
    if not text:
        return SearchCriteria(max_results_per_target=max_results_per_target)

    data = generate_json(_PROMPT.format(text=text))
    if not data or not isinstance(data, dict):
        criteria = _heuristic(text)
    else:
        criteria = SearchCriteria.from_dict({**data, "raw_text": text})

    criteria.raw_text = text
    criteria.max_results_per_target = max_results_per_target
    backup = _heuristic(text)
    if not criteria.targets:
        criteria.targets = backup.targets
    if not criteria.location:
        criteria.location = backup.location
    if not criteria.product:
        criteria.product = backup.product
    return criteria
