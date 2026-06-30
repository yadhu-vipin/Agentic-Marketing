"""
MarketingOrchestrator — workflow registry and executor.

Responsibilities:
  1. Maintain a registry of workflow_name → Workflow.
  2. Execute a named workflow against a CampaignState.
  3. Register new workflows via register().

The orchestrator has ZERO knowledge of individual capabilities or services.
Adding a new workflow requires only one new import in _register_defaults().
"""

import logging
from marketing_agent.state import CampaignState
from marketing_agent.workflows.base import Workflow

logger = logging.getLogger(__name__)


class MarketingOrchestrator:

    def __init__(self) -> None:
        self._registry: dict[str, Workflow] = {}
        self._register_defaults()

    # ── Public API ───────────────────────────────────────────────────────────────

    def register(self, workflow: Workflow) -> None:
        """Register a workflow under its name. Replaces any existing entry."""
        self._registry[workflow.name] = workflow
        logger.info("[orchestrator] registered workflow: %s", workflow.name)

    def available_workflows(self) -> list[str]:
        return list(self._registry.keys())

    async def run(self, workflow_name: str, state: CampaignState) -> CampaignState:
        """Execute a named workflow. Raises ValueError for unknown names."""
        workflow = self._registry.get(workflow_name)
        if not workflow:
            raise ValueError(
                f"Unknown workflow '{workflow_name}'. "
                f"Available: {self.available_workflows()}"
            )
        logger.info(
            "[orchestrator] executing workflow=%s campaign=%s",
            workflow_name,
            state.campaign_id,
        )
        return await workflow.execute(state)

    # ── Default registration ─────────────────────────────────────────────────────

    def _register_defaults(self) -> None:
        """
        Register all built-in workflows.
        Add one import + register() call here when a new workflow is created.
        """
        from marketing_agent.workflows.organic_campaign import OrganicCampaignWorkflow
        from marketing_agent.workflows.lead_generation import LeadGenerationWorkflow
        from marketing_agent.workflows.content_only import ContentOnlyWorkflow
        from marketing_agent.workflows.performance_campaign import PerformanceCampaignWorkflow

        for wf in [
            OrganicCampaignWorkflow(),
            LeadGenerationWorkflow(),
            ContentOnlyWorkflow(),
            PerformanceCampaignWorkflow(),
        ]:
            self.register(wf)
