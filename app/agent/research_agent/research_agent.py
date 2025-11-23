from app.agent.base_agent import BaseAgent
from app.agent.research_agent.config import load_research_agent_config
from app.agent.research_agent.state import ResearchAgentState, ResearchAgentInputState, ResearchAgentOutputState
from app.agent.research_agent.model import ResearchGenerationResponse
from app.common.llm import get_llm
from app.common.logging_config import get_logger
from typing import Any
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import SystemMessage, HumanMessage

logger = get_logger(__name__)


class ResearchAgent(BaseAgent):
    def __init__(self):
        logger.info("Initializing Research Agent")
        self._config = load_research_agent_config()
        self._prompt_config = self._config.RESEARCH_ANALYZER

        super().__init__("Research Agent", None)

        self.name = "Research Agent"
        self.llm = self._create_llm()

        model_name = self._prompt_config.model
        temperature = getattr(self._prompt_config, "temperature", 0)
        logger.info(
            f"Research Agent initialized - Model: {model_name}, Temperature: {temperature}"
        )

    def _create_llm(self) -> Any:
        """Create and configure the LLM instance."""
        temperature = getattr(self._prompt_config, "temperature", 0)
        model_name = self._prompt_config.model

        logger.debug(f"Creating LLM - Model: {model_name}, Temperature: {temperature}")

        # Create and return the LLM using the common utility
        llm = get_llm(model_name=model_name, temperature=temperature)

        # Add structured output if needed
        llm_with_structure = llm.with_structured_output(ResearchGenerationResponse)

        logger.debug("LLM created with structured output")
        return llm_with_structure

    def _create_streaming_llm(self) -> Any:
        """Create and configure the LLM instance for streaming (without structured output)."""
        temperature = getattr(self._prompt_config, "temperature", 0)
        model_name = self._prompt_config.model

        logger.debug(f"Creating streaming LLM - Model: {model_name}, Temperature: {temperature}")

        # Create and return the LLM for streaming (no structured output)
        llm = get_llm(model_name=model_name, temperature=temperature)

        logger.debug("Streaming LLM created")
        return llm

    async def _research_node(self, state: ResearchAgentState) -> dict:
        """Node that performs the research task."""
        user_input = state.get("user_input", "")
        input_preview = user_input[:100] + "..." if len(user_input) > 100 else user_input

        logger.debug(f"Research node execution started - Input: '{input_preview}' (length: {len(user_input)})")

        # Build messages for the LLM
        messages = []

        # Add system prompt if available
        if self._prompt_config.system_prompt:
            messages.append(SystemMessage(content=self._prompt_config.system_prompt))

        # Add user prompt
        if self._prompt_config.user_prompt_template:
            user_content = self._prompt_config.user_prompt_template.format(user_input=user_input)
        else:
            user_content = user_input

        messages.append(HumanMessage(content=user_content))

        # Invoke the LLM
        logger.debug("Invoking LLM for research")
        try:
            response: ResearchGenerationResponse = await self.llm.ainvoke(messages)

            summary_length = len(response.processing_summary or "")
            logger.info(f"LLM invocation completed - Summary length: {summary_length} chars")

            # Return the updated state
            return {
                "research_summary": response.processing_summary or "",
                "research_documents": response.research_document or "",
                "messages": messages
            }
        except Exception as e:
            logger.error(f"LLM invocation failed - Error: {str(e)}", exc_info=True)
            raise

    async def build_agent(self) -> StateGraph:
        """Build the Research Agent graph."""
        logger.debug("Building Research Agent graph")

        # Create the state graph
        workflow = StateGraph(
            ResearchAgentState,
            input=ResearchAgentInputState,
            output=ResearchAgentOutputState
        )

        # Add the research node
        workflow.add_node("research", self._research_node)

        # Define the flow: START -> research -> END
        workflow.add_edge(START, "research")
        workflow.add_edge("research", END)

        # Compile the graph
        self.agent = workflow.compile()

        logger.info("Research Agent graph compiled successfully")
        return self.agent

    async def invoke(self, data: Any) -> Any:
        """Invoke the Research Agent on input data."""
        logger.debug(f"Agent invoke called - Data type: {type(data).__name__}")

        # Ensure the agent is built
        if self.agent is None:
            logger.debug("Agent not built yet, building now")
            await self.build_agent()

        # Prepare the input state
        if isinstance(data, dict):
            input_state = data
        else:
            input_state = {"user_input": str(data)}

        # Invoke the agent
        try:
            result = await self.agent.ainvoke(input_state)
            logger.info("Agent invocation completed")
            return result
        except Exception as e:
            logger.error(f"Agent invocation failed - Error: {str(e)}", exc_info=True)
            raise

    async def stream_invoke(self, data: Any):
        """Stream the Research Agent execution with token-by-token output."""
        chunk_count = 0

        logger.debug(f"Agent stream_invoke called - Data type: {type(data).__name__}")

        # Ensure the agent is built
        if self.agent is None:
            logger.debug("Agent not built yet, building now")
            await self.build_agent()

        # Prepare the input state
        if isinstance(data, dict):
            input_state = data
        else:
            input_state = {"user_input": str(data)}

        # Create streaming LLM for this invocation
        streaming_llm = self._create_streaming_llm()

        # Build messages for the LLM
        user_input = input_state.get("user_input", "")
        messages = []

        # Add system prompt if available
        if self._prompt_config.system_prompt:
            messages.append(SystemMessage(content=self._prompt_config.system_prompt))

        # Add user prompt
        if self._prompt_config.user_prompt_template:
            user_content = self._prompt_config.user_prompt_template.format(user_input=user_input)
        else:
            user_content = user_input

        messages.append(HumanMessage(content=user_content))

        # Stream the LLM response
        logger.debug("Starting LLM streaming")
        accumulated_content = ""

        try:
            async for chunk in streaming_llm.astream(messages):
                if hasattr(chunk, 'content') and chunk.content:
                    accumulated_content += chunk.content
                    chunk_count += 1
                    yield {
                        "type": "text",
                        "content": chunk.content
                    }

            logger.info(
                f"Streaming completed - Chunks: {chunk_count}, "
                f"Content length: {len(accumulated_content)} chars"
            )

            # Send final complete message
            yield {
                "type": "done",
                "content": accumulated_content,
                "research_summary": accumulated_content[:500] if accumulated_content else "",
                "research_documents": accumulated_content
            }

        except Exception as e:
            logger.error(
                f"Streaming failed - Chunks sent: {chunk_count}, Error: {str(e)}",
                exc_info=True
            )
            raise