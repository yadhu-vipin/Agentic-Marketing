"""Research models — SearchCriteria and ResearchResult."""

from typing import Optional, List
from pydantic import BaseModel, Field


class SearchCriteria(BaseModel):
    raw_text: str = ""
    company_name: str = ""
    what_they_do: str = ""
    product: str = ""
    targets: List[str] = Field(default_factory=list)        # business types to search
    target_types: List[str] = Field(default_factory=list)   # target types for compatibility
    location: str = ""
    attributes: List[str] = Field(default_factory=list)     # desired lead qualities
    additional_requirements: str = ""
    max_results_per_target: int = 5

    def to_dict(self) -> dict:
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict) -> "SearchCriteria":
        allowed = {f for f in cls.model_fields}
        return cls(**{k: v for k, v in (data or {}).items() if k in allowed})

    def search_terms(self) -> list[str]:
        """Targets to iterate over; falls back to the product if none inferred."""
        return self.targets or self.target_types or ([self.product] if self.product else [])


class ResearchResult(BaseModel):
    criteria: SearchCriteria
    leads: list = []            # list[Lead] — avoid circular import
    summary: Optional[str] = None

