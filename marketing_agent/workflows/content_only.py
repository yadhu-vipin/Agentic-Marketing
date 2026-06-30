"""
ContentOnlyWorkflow — Plan → Generate content. No research, no publishing.

Steps:  PlanningCapability → ContentCapability
Input:  product_name, product_description, platforms
Output: state.assets (ready for human review before publishing)
"""

from marketing_agent.capabilities.content import ContentCapability
from marketing_agent.capabilities.planning import PlanningCapability
from marketing_agent.services.llm.gemini import GeminiLLMService
from marketing_agent.workflows.base import Workflow


class ContentOnlyWorkflow(Workflow):
    name = "content_only"

    def __init__(self) -> None:
        super().__init__()
        llm = GeminiLLMService()
        self.capabilities = [
            PlanningCapability(llm),
            ContentCapability(llm),
        ]
