"""ScoringCapability — scores leads for product fit using LLM."""

import logging
from marketing_agent.capabilities.base import Capability
from marketing_agent.services.llm.base import LLMService
from marketing_agent.state import CampaignState

logger = logging.getLogger(__name__)


class ScoringCapability(Capability):
    name = "scoring"

    def __init__(self, llm: LLMService) -> None:
        self._llm = llm

    async def _execute(self, state: CampaignState) -> CampaignState:
        for lead in state.leads:
            prompt = (
                f"Score this business lead from 0–100 for fit with the following product.\n"
                f"Product: {state.product_description}\n"
                f"Lead: {lead.model_dump()}\n\n"
                "Return JSON: {score: int, reason: str}"
            )
            data = await self._llm.generate_json(prompt)
            lead.score = int(data.get("score", 0))
            lead.score_reason = data.get("reason", "")

        scored = [l for l in state.leads if l.score is not None]
        logger.info("[ScoringCapability] scored %d leads", len(scored))
        return state
