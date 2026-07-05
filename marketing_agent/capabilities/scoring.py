"""
ScoringCapability — scores leads for product fit using LLM or heuristic fallbacks.
"""

import json
import logging

from marketing_agent.capabilities.base import Capability
from marketing_agent.models.lead import Lead
from marketing_agent.models.research import SearchCriteria
from marketing_agent.services.llm.base import LLMService
from marketing_agent.services.scraper.site_analyzer import generate_json
from marketing_agent.state import CampaignState

logger = logging.getLogger(__name__)

_BATCH_PROMPT = """Score each B2B lead from 0-100 for how well it fits the seller.

Seller wants to sell: {product}
What seller does: {what_they_do}
Target business types: {targets}
Location preference: {location}
Desired lead attributes: {attributes}
Extra requirements: {extra}

Judge relevance, buying potential, location fit, industry fit, and estimated
business size for each lead.

Leads (JSON array, each has an "i" index):
{leads}

Return a JSON array only, one object per lead:
[{{"i": <index>, "score": <0-100>, "priority": "high|medium|low", "reason": "<one sentence>",
   "strengths": ["..."], "gaps": ["..."]}}]"""

_DATA_FACTORS = (
    ("phone", "Phone number", 15),
    ("email", "Email address", 10),
    ("website", "Website", 10),
    ("address", "Address", 5),
    ("category", "Business category", 5),
)


def _priority(score: int) -> str:
    return "high" if score >= 70 else "medium" if score >= 45 else "low"


def _lead_fields(lead: Lead) -> dict:
    return {
        k: v
        for k, v in {
            "name": lead.name,
            "category": lead.category,
            "address": lead.address,
            "phone": lead.phone,
            "email": lead.email,
            "website": lead.website,
            "rating": lead.rating,
            "reviews": lead.reviews,
        }.items()
        if v is not None
    }


def _lead_blob(lead: Lead) -> str:
    return f"{lead.name} {lead.category or ''} {lead.address or ''}".lower()


def _has_field(lead: Lead, key: str) -> bool:
    val = getattr(lead, key, None)
    return bool(val and str(val).strip())


def _data_factors(lead: Lead) -> tuple[list[dict], list[str], list[str], int]:
    factors: list[dict] = []
    missing: list[str] = []
    present: list[str] = []
    points = 0

    for key, label, max_pts in _DATA_FACTORS:
        ok = _has_field(lead, key)
        pts = max_pts if ok else 0
        points += pts
        entry = {
            "key": key,
            "label": label,
            "present": ok,
            "points": pts,
            "max_points": max_pts,
            "group": "data",
        }
        factors.append(entry)
        if ok:
            present.append(label)
        else:
            missing.append(label)

    if lead.rating:
        if lead.rating >= 4.3:
            rating_pts, rating_label = 20, f"Strong rating ({lead.rating}★)"
        elif lead.rating >= 3.8:
            rating_pts, rating_label = 10, f"Good rating ({lead.rating}★)"
        else:
            rating_pts, rating_label = 0, f"Low rating ({lead.rating}★)"
        points += rating_pts
        factors.append(
            {
                "key": "rating",
                "label": rating_label,
                "present": rating_pts > 0,
                "points": rating_pts,
                "max_points": 20,
                "group": "quality",
            }
        )
        if rating_pts:
            present.append(rating_label)
        else:
            missing.append("Higher Google rating (≥3.8★)")
    else:
        factors.append(
            {
                "key": "rating",
                "label": "Google rating",
                "present": False,
                "points": 0,
                "max_points": 20,
                "group": "quality",
            }
        )
        missing.append("Google rating")

    return factors, missing, present, points


def _criteria_factors(
    lead: Lead, criteria: SearchCriteria
) -> tuple[list[dict], list[str], list[str], int]:
    factors: list[dict] = []
    matched: list[str] = []
    gaps: list[str] = []
    points = 0
    blob = _lead_blob(lead)

    targets = criteria.targets or []
    for target in targets:
        ok = target.lower() in blob or (
            lead.category and target.lower() in lead.category.lower()
        )
        label = f"Target type: {target}"
        factors.append(
            {
                "key": f"target:{target}",
                "label": label,
                "present": ok,
                "points": 8 if ok else 0,
                "max_points": 8,
                "group": "fit",
            }
        )
        if ok:
            matched.append(label)
            points += 8
        else:
            gaps.append(label)

    if criteria.location:
        loc = criteria.location.lower()
        ok = loc in blob
        label = f"Location: {criteria.location}"
        factors.append(
            {
                "key": "location",
                "label": label,
                "present": ok,
                "points": 10 if ok else 0,
                "max_points": 10,
                "group": "fit",
            }
        )
        if ok:
            matched.append(label)
            points += 10
        else:
            gaps.append(label)

    attributes = criteria.attributes or []
    attr_matches = [a for a in attributes if a.lower() in blob]
    attr_gaps = [a for a in attributes if a.lower() not in blob]
    if attributes:
        factors.append(
            {
                "key": "attributes",
                "label": "Desired attributes",
                "present": bool(attr_matches),
                "points": 10 if attr_matches else 0,
                "max_points": 10,
                "group": "fit",
                "matched": attr_matches,
                "missing": attr_gaps,
            }
        )
        if attr_matches:
            matched.extend(attr_matches)
            points += 10
        for gap in attr_gaps:
            gaps.append(f"Attribute: {gap}")

    return factors, matched, gaps, points


def _build_breakdown(
    lead: Lead,
    criteria: SearchCriteria,
    *,
    base_score: int = 30,
    ai_strengths: list[str] | None = None,
    ai_gaps: list[str] | None = None,
) -> dict:
    data_factors, data_missing, data_present, data_pts = _data_factors(lead)
    fit_factors, fit_matched, fit_gaps, fit_pts = _criteria_factors(lead, criteria)
    factors = data_factors + fit_factors
    total = min(100, max(0, base_score + data_pts + fit_pts))

    missing_fields = [f["label"] for f in data_factors if not f["present"]]
    missing_all = missing_fields + fit_gaps
    if ai_gaps:
        for gap in ai_gaps:
            if gap not in missing_all:
                missing_all.append(gap)

    strengths = list(data_present + fit_matched)
    if ai_strengths:
        for s in ai_strengths:
            if s not in strengths:
                strengths.append(s)

    summary_parts = []
    if missing_all:
        summary_parts.append("Missing: " + ", ".join(missing_all[:5]))
        if len(missing_all) > 5:
            summary_parts[-1] += f" (+{len(missing_all) - 5} more)"
    if strengths:
        summary_parts.append("Has: " + ", ".join(strengths[:4]))

    attributes = criteria.attributes or []
    return {
        "total": total,
        "base_points": base_score,
        "factors": factors,
        "missing_fields": missing_fields,
        "missing": missing_all,
        "present": strengths,
        "attribute_matches": [a for a in attributes if a.lower() in _lead_blob(lead)],
        "attribute_gaps": [a for a in attributes if a.lower() not in _lead_blob(lead)],
        "strengths": strengths,
        "gaps": missing_all,
        "summary": ". ".join(summary_parts) if summary_parts else "Limited data available",
    }


def _apply_heuristic(lead: Lead, criteria: SearchCriteria) -> Lead:
    breakdown = _build_breakdown(lead, criteria)
    lead.score = breakdown["total"]
    lead.priority = _priority(lead.score)
    lead.score_breakdown = breakdown
    lead.score_reason = breakdown["summary"]
    return lead


def _apply_ai(lead: Lead, result: dict, criteria: SearchCriteria) -> Lead:
    score = max(0, min(int(result.get("score", 0)), 100))
    priority = result.get("priority")
    raw_strengths = result.get("strengths")
    strengths = raw_strengths if isinstance(raw_strengths, list) else []
    raw_gaps = result.get("gaps")
    gaps = raw_gaps if isinstance(raw_gaps, list) else []

    breakdown = _build_breakdown(
        lead,
        criteria,
        base_score=0,
        ai_strengths=[str(s) for s in strengths],
        ai_gaps=[str(g) for g in gaps],
    )
    breakdown["total"] = score
    breakdown["mode"] = "ai"
    if result.get("reason"):
        breakdown["ai_reason"] = str(result["reason"])

    lead.score = score
    lead.priority = priority if priority in ("high", "medium", "low") else _priority(score)
    lead.score_breakdown = breakdown
    reason = result.get("reason", "")
    if breakdown["missing"]:
        lead.score_reason = f"{reason} Missing: {', '.join(breakdown['missing'][:4])}."
    else:
        lead.score_reason = reason or breakdown["summary"]
    return lead


def _criteria_from_state(state: CampaignState) -> SearchCriteria:
    targets = (
        [t.strip() for t in state.target_audience.split(",") if t.strip()]
        if state.target_audience
        else []
    )
    return SearchCriteria(
        company_name=state.product_name,
        product=state.product_description or state.product_name,
        targets=targets,
        location=state.location or "",
        attributes=[],
    )


class ScoringCapability(Capability):
    name = "scoring"

    def __init__(self, llm: LLMService | None = None) -> None:
        self._llm = llm

    async def _execute(self, state: CampaignState) -> CampaignState:
        if not state.leads:
            logger.info("[ScoringCapability] no leads to score")
            return state

        criteria = _criteria_from_state(state)

        # Batch scoring prompt
        items = [{"i": idx, **_lead_fields(lead)} for idx, lead in enumerate(state.leads)]
        result = generate_json(
            _BATCH_PROMPT.format(
                product=criteria.product or "(unspecified)",
                what_they_do=state.product_description or "(unspecified)",
                targets=", ".join(criteria.targets) or "(any)",
                location=criteria.location or "(any)",
                attributes="",
                extra="",
                leads=json.dumps(items)[:6000],
            )
        )

        by_index = {}
        if isinstance(result, list):
            by_index = {r.get("i"): r for r in result if isinstance(r, dict) and "score" in r}

        for idx, lead in enumerate(state.leads):
            if idx in by_index:
                _apply_ai(lead, by_index[idx], criteria)
            else:
                _apply_heuristic(lead, criteria)

        state.leads.sort(key=lambda x: x.score or 0, reverse=True)
        logger.info("[ScoringCapability] scored %d leads", len(state.leads))
        return state
