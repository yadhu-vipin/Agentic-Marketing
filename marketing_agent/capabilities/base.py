"""
Capability ABC — stateless, composable unit of work.

Rules:
- Must not hold mutable instance state between calls.
- Reads from CampaignState, writes output fields back, returns the same object.
- All logging and timing is handled by the base class execute() wrapper.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from marketing_agent.state import CampaignState

logger = logging.getLogger(__name__)


class Capability(ABC):
    name: str = "capability"

    async def execute(self, state: "CampaignState") -> "CampaignState":  # type: ignore[name-defined]
        logger.info("[capability:%s] started — campaign=%s", self.name, state.campaign_id)
        start = time.monotonic()
        state.add_log(f"capability:{self.name} started")
        try:
            state = await self._execute(state)
            elapsed = time.monotonic() - start
            logger.info("[capability:%s] completed in %.2fs", self.name, elapsed)
            state.add_log(f"capability:{self.name} completed ({elapsed:.2f}s)")
        except Exception as exc:
            logger.error("[capability:%s] failed: %s", self.name, exc, exc_info=True)
            state.fail(f"capability:{self.name} → {exc}")
            raise
        return state

    @abstractmethod
    async def _execute(self, state: "CampaignState") -> "CampaignState":  # type: ignore[name-defined]
        ...
