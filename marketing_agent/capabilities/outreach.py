"""
OutreachCapability — drafts personalised email and WhatsApp messages per lead.
"""

import json
import logging

from marketing_agent.capabilities.base import Capability
from marketing_agent.models.lead import Lead
from marketing_agent.models.research import SearchCriteria
from marketing_agent.services.llm.base import LLMService
from marketing_agent.services.publishing.image_generator import generate_ad_image
from marketing_agent.state import CampaignState

logger = logging.getLogger(__name__)

_PROMPT = """Write personalized B2B outreach for this lead. Reference real details
naturally; keep it warm, concise, and specific. No placeholders.
{image_note}

Seller: {company} — sells {product} ({what_they_do})
Seller location: {location}

Lead:
{lead}

Return JSON only:
{{"email": "<subject + body, 80-130 words>", "whatsapp": "<short 2-3 line message>"}}"""


def _fallback(lead: Lead, criteria: SearchCriteria, *, image_note: str = "") -> dict:
    company = criteria.company_name or "our team"
    product = criteria.product or "our products"
    rating_line = f" Your {lead.rating}★ reputation stood out." if lead.rating else ""
    attach_line = "\n\nI've attached a preview image of our product." if image_note else ""
    email = (
        f"Subject: {product.title()} for {lead.name}\n\n"
        f"Hi {lead.name} team,\n\n"
        f"I'm reaching out from {company}. We supply {product} and thought it could be "
        f"a great fit for {lead.category or 'your business'}"
        f"{f' in {lead.address}' if lead.address else ''}.{rating_line}\n\n"
        f"Would you be open to a quick chat or a free sample this week?{attach_line}\n\n"
        f"Warm regards,\n{company}"
    )
    whatsapp = (
        f"Hi {lead.name}! {company} here — we supply {product} and would love to work with you. "
        f"Open to a quick chat or a free sample?"
    )
    return {"email": email, "whatsapp": whatsapp}


def _per_lead_image_prompt(lead: Lead, criteria: SearchCriteria) -> str:
    product = criteria.product or "premium product"
    category = lead.category or "business"
    return (
        f"Professional marketing photo for {product}, appealing to {category} "
        f"named {lead.name}, clean modern style, no text overlay"
    )


def _resolve_image(
    *,
    image_mode: str,
    campaign_ad: dict | None,
    lead: Lead,
    criteria: SearchCriteria,
) -> dict | None:
    if image_mode == "campaign" and campaign_ad and campaign_ad.get("image_url"):
        return {
            "image_url": campaign_ad["image_url"],
            "image_mode": "campaign",
            "image_prompt": campaign_ad.get("image_prompt", ""),
        }
    if image_mode == "per_lead":
        prompt = _per_lead_image_prompt(lead, criteria)
        img = generate_ad_image(prompt)
        return {
            "image_url": img["image_url"],
            "image_mode": "per_lead",
            "image_prompt": prompt,
        }
    return None


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


class OutreachCapability(Capability):
    name = "outreach"

    def __init__(self, llm: LLMService) -> None:
        self._llm = llm

    async def _execute(self, state: CampaignState) -> CampaignState:
        if not state.leads:
            logger.info("[OutreachCapability] no leads to generate outreach for")
            return state

        criteria = _criteria_from_state(state)

        # Retrieve campaign ad asset if available
        campaign_ad = None
        if state.assets:
            # Look for a content asset with platform and creative_url
            for asset in state.assets:
                if getattr(asset, "creative_url", None):
                    campaign_ad = {
                        "image_url": asset.creative_url,
                        "image_prompt": getattr(asset, "creative_prompt", ""),
                    }
                    break

        image_mode = getattr(state, "image_mode", "none")
        instructions = getattr(state, "instructions", "")

        for lead in state.leads:
            meta = lead.metadata or {}
            payload = json.dumps(
                {
                    k: v
                    for k, v in {
                        "name": lead.name,
                        "category": lead.category,
                        "address": lead.address,
                        "rating": lead.rating,
                        "website": lead.website,
                        "score_reason": lead.score_reason,
                        "site_summary": meta.get("site_summary"),
                        "site_services": meta.get("site_services"),
                    }.items()
                    if v is not None
                },
                indent=2,
            )[:1500]

            image_info = _resolve_image(
                image_mode=image_mode,
                campaign_ad=campaign_ad,
                lead=lead,
                criteria=criteria,
            )
            image_note = ""
            if image_info:
                image_note = (
                    "An image will be attached to the email. Mention it naturally once "
                    f"(prompt: {image_info.get('image_prompt', '')[:120]})."
                )

            extra_instructions = (
                f"\n\nAdditional instructions from the user:\n{instructions.strip()}"
                if instructions.strip()
                else ""
            )

            prompt = (
                _PROMPT.format(
                    company=criteria.company_name or "our team",
                    product=criteria.product or "our products",
                    what_they_do=state.product_description or "",
                    location=criteria.location or "",
                    lead=payload,
                    image_note=image_note,
                )
                + extra_instructions
            )

            result = await self._llm.generate_json(prompt)

            if result and isinstance(result, dict) and result.get("email"):
                outreach = {
                    "email": result.get("email", ""),
                    "whatsapp": result.get("whatsapp", ""),
                }
            else:
                outreach = _fallback(lead, criteria, image_note=image_note)

            if image_info:
                outreach.update(image_info)

            lead.outreach = outreach

        logger.info("[OutreachCapability] drafted messages for %d leads", len(state.leads))
        return state
