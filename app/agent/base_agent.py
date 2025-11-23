from abc import ABC, abstractmethod
from typing import Any, Optional

from langchain_core.language_models.chat_models import BaseChatModel


class BaseAgent(ABC):
    """Abstract base class for AI agents.

    This class defines the interface that all agent implementations must follow.
    Subclasses can either provide an LLM instance during initialization or
    create one internally by implementing the _create_llm method.
    """

    def __init__(self, name: str, llm: Optional[BaseChatModel] = None):
        """Initialize the agent.

        Args:
            name: Name of the agent
            llm: Optional LLM instance. If not provided, subclass must implement
                 _create_llm() method to create the LLM instance.
        """
        self.name = name
        self.agent = None

        # Allow subclasses to create their own LLM if not provided
        if llm is not None:
            self.llm = llm
        else:
            self.llm = self._create_llm()

    def _create_llm(self) -> BaseChatModel:
        """Create and return an LLM instance.

        This method can be overridden by subclasses that need to create
        their own LLM configuration. If not overridden and no LLM is provided
        in __init__, this will raise NotImplementedError.

        Returns:
            BaseChatModel: Configured LLM instance

        Raises:
            NotImplementedError: If not implemented by subclass and no LLM provided
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must either provide an llm parameter "
            "or implement the _create_llm() method"
        )

    @abstractmethod
    async def build_agent(self):
        """Build the agent graph. Must be implemented by subclasses.

        Returns:
            StateGraph: The compiled agent graph.
        """
        pass

    @abstractmethod
    async def invoke(self, data: Any):
        """Invoke the agent on input data. Must be implemented by subclasses.

        Args:
            data: The input data to process.

        Returns:
            The agent response.
        """
        pass

    @abstractmethod
    async def stream_invoke(self, data: Any):
        """Stream the agent execution with token-by-token output.

        Must be implemented by subclasses.

        Args:
            data: The input data to process.

        Yields:
            Dict with streaming events (tokens, status, etc.)
        """
        pass
