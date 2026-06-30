"""OutreachCapability — drafts personalised email and WhatsApp messages per lead."""

import logging
from marketing_agent.capabilities.base import Capability
from marketing_agent.services.llm.base import LLMService
from marketing_agent.state import CampaignState

logger = logging.getLogger(__name__)


class OutreachCapability(Capability):
    name = "outreach"

    def __init__(self, llm: LLMService) -> None:
        self._llm = llm

    async def _execute(self, state: CampaignState) -> CampaignState:
        for lead in state.leads:
            prompt = (
                f"Write a personalised outreach message for the following business.\n"
                f"Product we are selling: {state.product_description}\n"
                f"Lead business: {lead.name} ({lead.category}), {lead.address}\n\n"
                "Return JSON: {email: str, whatsapp: str}"
            )
            data = await self._llm.generate_json(prompt)
            lead.email_draft = data.get("email", "")
            lead.whatsapp_draft = data.get("whatsapp", "")

        logger.info("[OutreachCapability] drafted messages for %d leads", len(state.leads))
        return state
