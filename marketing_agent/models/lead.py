"""Lead model — moved from legacy/fastapi-leadgen/src/shared/models/lead.py"""

from typing import Optional
from pydantic import BaseModel


class Lead(BaseModel):
    name: str
    category: str = ""
    address: str = ""
    phone: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[float] = None
    reviews: Optional[int] = None
    source: str = ""
    score: Optional[int] = None
    score_reason: Optional[str] = None
    email_draft: Optional[str] = None
    whatsapp_draft: Optional[str] = None
    whatsapp_opt_in: bool = False
