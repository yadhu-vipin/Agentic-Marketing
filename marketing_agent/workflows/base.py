"""
Workflow base class — ordered composition of Capability instances.

A workflow has no logic of its own. It executes each capability in sequence,
passing the same CampaignState through every step. If any capability marks
the state as failed, execution halts.
"""

import logging
from marketing_agent.capabilities.base import Capability
from marketing_agent.state import CampaignState

logger = logging.getLogger(__name__)


class Workflow:
    name: str = "workflow"
    capabilities: list[Capability]

    def __init__(self) -> None:
        self.capabilities = []

    async def execute(self, state: CampaignState) -> CampaignState:
        state.workflow_name = self.name
        state.status = "running"
        logger.info(
            "[workflow:%s] started — campaign=%s steps=%d",
            self.name,
            state.campaign_id,
            len(self.capabilities),
        )

        for capability in self.capabilities:
            if state.status == "failed":
                logger.warning(
                    "[workflow:%s] halting — prior step failed before %s",
                    self.name,
                    capability.name,
                )
                break
            state = await capability.execute(state)

        if state.status != "failed":
            state.status = "completed"

        logger.info("[workflow:%s] finished — status=%s", self.name, state.status)
        return state
