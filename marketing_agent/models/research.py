"""Research models — SearchCriteria and ResearchResult."""

from typing import Optional
from pydantic import BaseModel


class SearchCriteria(BaseModel):
    product: str
    target_types: list[str] = []
    location: str = ""
    max_results_per_target: int = 5


class ResearchResult(BaseModel):
    criteria: SearchCriteria
    leads: list = []            # list[Lead] — avoid circular import
    summary: Optional[str] = None
