"""LLMService ABC — no capability or workflow imports this SDK directly."""

from abc import ABC, abstractmethod


class LLMService(ABC):
    @abstractmethod
    async def generate_text(self, prompt: str) -> str:
        """Return a plain-text response for the given prompt."""
        ...

    @abstractmethod
    async def generate_json(self, prompt: str) -> dict:
        """Return a parsed JSON dict for the given prompt."""
        ...
