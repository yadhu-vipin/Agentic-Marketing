"""Lead model."""

import uuid
from typing import Optional
from pydantic import BaseModel, Field


class Lead(BaseModel):
    name: str
    category: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    send_to_email: Optional[str] = None  # override recipient for outreach / Gmail
    rating: Optional[float] = None
    reviews: Optional[int] = None
    source: str = "unknown"
    metadata: dict = Field(default_factory=dict)

    # ── Added by AI stages ─────────────────────────────────────────────────
    score: Optional[int] = None
    score_reason: Optional[str] = None
    score_breakdown: dict = Field(default_factory=dict)  # factors, missing, strengths
    priority: Optional[str] = None
    outreach: dict = Field(default_factory=dict)   # {"email": ..., "whatsapp": ...}

    # ── Phase 2/3: campaign + funnel ─────────────────────────────────────
    campaign_id: Optional[str] = None
    funnel_status: str = "scraped"       # scraped | scored | outreached | opened | replied | converted
    whatsapp_opt_in: bool = False
    outreach_status: str = "draft"       # draft | pending_approval | sent | failed

    # ── Lead list triage ───────────────────────────────────────────────────
    list_status: str = "inbox"           # inbox | stored | discarded | cleared

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])

    def to_dict(self) -> dict:
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict) -> "Lead":
        allowed = {f for f in cls.model_fields}
        return cls(**{k: v for k, v in (data or {}).items() if k in allowed})

