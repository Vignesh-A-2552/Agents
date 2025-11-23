from abc import ABC,abstractmethod
from langchain_core.language_models.chat_models import BaseChatModel
from typing import Any

class BaseAgent(ABC):

    def __init__(self, name: str, llm:BaseChatModel):
        self.name = name
        self.llm = llm
        self.agent = None

    @abstractmethod
    async def build_agent(self):
        """
        Build the agent graph. Must be implemented by subclasses.

        Returns:
            StateGraph: The compiled agent graph.
        """
        pass

    @abstractmethod
    async def invoke(self, data: Any):
        """
        Invoke the agent on input data. Must be implemented by subclasses.

        Args:
            data: The input data to process.
            **kwargs: Additional keyword arguments.

        Returns:
            The agent response.
        """
        pass

    @abstractmethod
    async def stream_invoke(self, data: Any):
        """
        Stream the agent execution with token-by-token output. Must be implemented by subclasses.

        Args:
            data: The input data to process.

        Yields:
            Dict with streaming events (tokens, status, etc.)
        """
        pass
