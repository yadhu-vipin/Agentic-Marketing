"""Domain exceptions for the marketing agent."""


class MarketingAgentError(Exception):
    """Base exception for all domain errors."""


class WorkflowNotFoundError(MarketingAgentError):
    """Raised when an unknown workflow name is requested."""


class PublishingError(MarketingAgentError):
    """Raised when a publisher fails to post content."""


class ScraperError(MarketingAgentError):
    """Raised when a scraper encounters an unrecoverable error."""


class LLMError(MarketingAgentError):
    """Raised when LLM generation fails or returns unparseable output."""


class ConfigurationError(MarketingAgentError):
    """Raised when required environment variables are missing."""
