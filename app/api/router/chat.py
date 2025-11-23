import json

from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse

from app.agent.research_agent.research_agent import ResearchAgent
from app.api.dependencies import get_research_agent
from app.common.exceptions import AgentException, LLMException, ValidationException
from app.common.logging_config import get_logger
from app.models.chat import ChatRequest, ChatResponse
from app.models.error import ErrorResponse

router = APIRouter(prefix="/api/v1")
logger = get_logger(__name__)


@router.post(
    "/chat/research",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    tags=["Chat"],
    summary="Research chat endpoint",
    description="Submit a research query and receive a comprehensive research summary with relevant documents.",
    responses={
        200: {
            "description": "Successful research response",
            "model": ChatResponse,
        },
        400: {
            "description": "Invalid request (e.g., empty query, query too long)",
            "model": ErrorResponse,
        },
        422: {
            "description": "Validation error",
            "model": ErrorResponse,
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse,
        },
        502: {
            "description": "LLM service error",
            "model": ErrorResponse,
        },
    },
)
async def research_chat(
    request: ChatRequest,
    agent: ResearchAgent = Depends(get_research_agent),
):
    """Research chat endpoint that uses the Research Agent.

    This endpoint processes a user query through the research agent workflow,
    which performs multi-step research and returns a comprehensive summary
    with supporting documents.

    Args:
        request: ChatRequest containing the user query
        agent: Injected ResearchAgent instance

    Returns:
        ChatResponse with research summary and documents

    Raises:
        ValidationException: If the query is invalid
        LLMException: If the LLM service fails
        AgentException: If the agent execution fails
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
            research_documents=result.get("research_documents", ""),
        )
    except ValueError as e:
        # Handle validation errors from the agent
        logger.warning(f"Validation error - Query: '{query_preview}', Error: {str(e)}")
        raise ValidationException(
            detail=str(e),
            extra={"query_length": len(request.query)},
        )
    except TimeoutError as e:
        # Handle timeout errors
        logger.error(f"Timeout - Query: '{query_preview}', Error: {str(e)}")
        raise LLMException(
            detail="Request timed out while processing your query",
            status_code=504,
            error_code="TIMEOUT",
        )
    except Exception as e:
        # Catch LLM-specific errors (could be from OpenAI, etc.)
        error_msg = str(e).lower()
        if any(
            keyword in error_msg
            for keyword in ["openai", "api", "rate limit", "quota", "timeout"]
        ):
            logger.error(f"LLM error - Query: '{query_preview}', Error: {str(e)}", exc_info=True)
            raise LLMException(
                detail="The AI service is currently unavailable. Please try again later.",
                extra={"error_type": e.__class__.__name__},
            )

        # Generic agent error
        logger.error(
            f"Agent invocation failed - Query: '{query_preview}', Error: {str(e)}",
            exc_info=True,
        )
        raise AgentException(
            detail="Failed to process your query. Please try again.",
            extra={"error_type": e.__class__.__name__},
        )


@router.post(
    "/chat/research/stream",
    status_code=status.HTTP_200_OK,
    tags=["Chat"],
    summary="Streaming research chat endpoint",
    description="Submit a research query and receive streaming responses with real-time LLM token generation.",
    responses={
        200: {
            "description": "Successful streaming response (text/event-stream)",
            "content": {"text/event-stream": {"example": 'data: {"type": "token", "content": "..."}\n\n'}},
        },
        400: {
            "description": "Invalid request",
            "model": ErrorResponse,
        },
        422: {
            "description": "Validation error",
            "model": ErrorResponse,
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse,
        },
    },
)
async def research_chat_stream(
    request: ChatRequest,
    agent: ResearchAgent = Depends(get_research_agent),
):
    """Streaming research chat endpoint that streams LLM tokens in real-time.

    This endpoint provides Server-Sent Events (SSE) streaming for real-time
    response generation. Events are sent in the format: `data: {json}\\n\\n`

    Event types:
    - token: Individual token from LLM generation
    - error: Error event if something goes wrong
    - done: Final event indicating completion

    Args:
        request: ChatRequest containing the user query
        agent: Injected ResearchAgent instance

    Returns:
        StreamingResponse with SSE (Server-Sent Events) format

    Raises:
        ValidationException: If the query is invalid
        AgentException: If the agent execution fails
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

        except ValueError as e:
            logger.warning(f"Validation error in stream - Query: '{query_preview}', Error: {str(e)}")
            error_event = json.dumps({
                "type": "error",
                "error": "VALIDATION_ERROR",
                "message": str(e),
            })
            yield f"data: {error_event}\n\n"
        except Exception as e:
            # Log full error details
            logger.error(
                f"Streaming failed - Events sent: {event_count}, Error: {str(e)}",
                exc_info=True,
            )

            # Determine error type
            error_msg = str(e).lower()
            if any(keyword in error_msg for keyword in ["openai", "api", "rate limit", "quota"]):
                error_type = "LLM_ERROR"
                user_message = "The AI service is currently unavailable"
            else:
                error_type = "AGENT_ERROR"
                user_message = "Failed to process your query"

            # Send sanitized error event to client
            error_event = json.dumps({
                "type": "error",
                "error": error_type,
                "message": user_message,
            })
            yield f"data: {error_event}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")