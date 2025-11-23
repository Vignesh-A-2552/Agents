from fastapi import APIRouter, Depends
from app.agent.research_agent.research_agent import ResearchAgent
from app.api.dependencies import get_research_agent
from app.models.chat import ChatRequest, ChatResponse
from fastapi.responses import StreamingResponse
from app.common.logging_config import get_logger
import json

router = APIRouter(prefix="/api/v1")
logger = get_logger(__name__)


@router.post("/chat/research", response_model=ChatResponse)
async def research_chat(
    request: ChatRequest,
    agent: ResearchAgent=Depends(get_research_agent)
):
    """
    Research chat endpoint that uses the Research Agent.

    Args:
        request: ChatRequest containing the user query

    Returns:
        ChatResponse with research summary and documents
    """
    query_preview = request.query[:100] + "..." if len(request.query) > 100 else request.query
    logger.info(f"Chat request received - Query: '{query_preview}' (length: {len(request.query)})")

    try:
        # Invoke the research agent
        logger.debug("Invoking research agent")
        result = await agent.invoke({"user_input": request.query})

        summary_length = len(result.get("research_summary", ""))
        logger.info(f"Agent invocation completed - Summary length: {summary_length} chars")

        # Return structured response
        return ChatResponse(
            research_summary=result.get("research_summary", ""),
            research_documents=result.get("research_documents", "")
        )
    except Exception as e:
        logger.error(
            f"Agent invocation failed - Query: '{query_preview}', Error: {str(e)}",
            exc_info=True
        )
        raise


@router.post("/chat/research/stream")
async def research_chat_stream(
    request: ChatRequest,
    agent: ResearchAgent=Depends(get_research_agent)
):
    """
    Streaming research chat endpoint that streams LLM tokens in real-time.

    Args:
        request: ChatRequest containing the user query

    Returns:
        StreamingResponse with SSE (Server-Sent Events) format
    """
    query_preview = request.query[:100] + "..." if len(request.query) > 100 else request.query
    logger.info(f"Streaming chat request received - Query: '{query_preview}' (length: {len(request.query)})")

    async def event_stream():
        """Generate SSE events from the agent's streaming response."""
        event_count = 0

        try:
            logger.debug("Starting streaming agent invocation")

            async for event in agent.stream_invoke({"user_input": request.query}):
                # Format as SSE: data: {json}\n\n
                event_data = json.dumps(event)
                yield f"data: {event_data}\n\n"
                event_count += 1

            logger.info(f"Streaming completed - Events sent: {event_count}")

        except Exception as e:
            logger.error(
                f"Streaming failed - Events sent: {event_count}, Error: {str(e)}",
                exc_info=True
            )
            # Send error event
            error_event = json.dumps({"type": "error", "message": str(e)})
            yield f"data: {error_event}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")