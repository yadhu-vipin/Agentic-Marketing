"""StorageService ABC."""

from abc import ABC, abstractmethod
from typing import Any


class StorageService(ABC):
    @abstractmethod
    async def save(self, key: str, data: Any) -> None:
        """Persist data under key."""
        ...

    @abstractmethod
    async def load(self, key: str) -> Any:
        """Load data stored under key. Returns None if not found."""
        ...
