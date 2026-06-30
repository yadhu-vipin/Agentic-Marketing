"""PlanningCapability — generates per-platform content briefs."""

import logging
from marketing_agent.capabilities.base import Capability
from marketing_agent.services.llm.base import LLMService
from marketing_agent.state import CampaignState

logger = logging.getLogger(__name__)


class PlanningCapability(Capability):
    name = "planning"

    def __init__(self, llm: LLMService) -> None:
        self._llm = llm

    async def _execute(self, state: CampaignState) -> CampaignState:
        prompt = (
            f"Create a per-platform content plan for the following product.\n"
            f"Product: {state.product_name}\n"
            f"Description: {state.product_description}\n"
            f"Audience: {state.target_audience or 'general'}\n"
            f"Industry: {state.industry or 'general'}\n"
            f"Platforms: {state.platforms}\n"
            f"Research summary: {state.research_summary or 'N/A'}\n\n"
            "Return a JSON array where each element has: "
            "platform, headline_direction, tone, key_message."
        )
        result = await self._llm.generate_json(prompt)
        state.content_plan = result if isinstance(result, list) else []
        logger.info(
            "[PlanningCapability] produced %d platform briefs", len(state.content_plan)
        )
        return state
