"""PublisherService ABC."""

from abc import ABC, abstractmethod

from marketing_agent.models.publishing import PublishRequest, PublishResult


class PublisherService(ABC):
    platform: str = "unknown"

    @abstractmethod
    async def publish(self, request: PublishRequest) -> PublishResult:
        """Publish the asset described in request. Return the result."""
        ...
