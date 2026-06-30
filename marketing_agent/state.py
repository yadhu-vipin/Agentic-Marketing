"""
CampaignState — the single shared context that flows through every capability
in a workflow. All capabilities read from and write to this object.
No capability communicates with another through any other mechanism.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from marketing_agent.models.analytics import AnalyticsReport
    from marketing_agent.models.content import ContentAsset
    from marketing_agent.models.lead import Lead
    from marketing_agent.models.publishing import PublishResult


class CampaignState(BaseModel):
    # ── Identity ─────────────────────────────────────────────────────────────────
    campaign_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_name: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # ── Input (supplied by caller, treated as immutable after workflow starts) ────
    product_name: str = ""
    product_description: str = ""
    target_audience: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    platforms: list[str] = []

    # ── Research outputs (written by ResearchCapability) ─────────────────────────
    leads: list[Any] = []           # list[Lead] — Any to avoid circular import
    research_summary: Optional[str] = None

    # ── Planning outputs (written by PlanningCapability) ─────────────────────────
    content_plan: list[dict] = []   # per-platform brief dicts

    # ── Content outputs (written by ContentCapability) ───────────────────────────
    assets: list[Any] = []          # list[ContentAsset]

    # ── Publishing outputs (written by PublishingCapability) ─────────────────────
    publish_results: list[Any] = [] # list[PublishResult]

    # ── Analytics outputs (written by AnalyticsCapability) ───────────────────────
    analytics: Optional[Any] = None # AnalyticsReport

    # ── Execution metadata ───────────────────────────────────────────────────────
    status: str = "pending"         # pending | running | completed | failed
    errors: list[str] = []
    log: list[str] = []

    def add_log(self, msg: str) -> None:
        self.log.append(f"{datetime.utcnow().isoformat()} {msg}")

    def fail(self, msg: str) -> None:
        self.status = "failed"
        self.errors.append(msg)
        self.add_log(f"FAILED: {msg}")
