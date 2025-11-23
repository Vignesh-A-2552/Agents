"""Global exception handlers for the Agents API.

This module provides centralized exception handling to ensure consistent
error responses across all API endpoints.
"""

import logging
from datetime import datetime
from typing import Union

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.common.exceptions import (
    APIException,
    AgentException,
    AuthenticationException,
    AuthorizationException,
    LLMException,
    NotFoundException,
    RateLimitException,
    TimeoutException,
    ValidationException,
)
from app.models.error import ErrorResponse, ValidationErrorDetail, ValidationErrorResponse

logger = logging.getLogger(__name__)


def get_request_id(request: Request) -> str:
    """Extract or generate a unique request ID for tracing."""
    return getattr(request.state, "request_id", "unknown")


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """Handle custom API exceptions.

    Args:
        request: The FastAPI request object
        exc: The custom API exception

    Returns:
        JSONResponse with standardized error format
    """
    request_id = get_request_id(request)

    # Log the error with full context
    logger.error(
        f"API Exception: {exc.error_code} - {exc.detail}",
        extra={
            "request_id": request_id,
            "status_code": exc.status_code,
            "error_code": exc.error_code,
            "path": request.url.path,
            "method": request.method,
            "extra": exc.extra,
        },
        exc_info=True,
    )

    error_response = ErrorResponse(
        error=exc.error_code,
        detail=exc.detail,
        timestamp=datetime.utcnow(),
        request_id=request_id,
        extra=exc.extra,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(mode="json"),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle FastAPI request validation errors (422).

    Args:
        request: The FastAPI request object
        exc: The validation error from Pydantic

    Returns:
        JSONResponse with detailed validation error information
    """
    request_id = get_request_id(request)

    # Parse Pydantic validation errors
    validation_errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        validation_errors.append(
            ValidationErrorDetail(
                field=field,
                message=error["msg"],
                type=error["type"],
            )
        )

    logger.warning(
        f"Validation error on {request.method} {request.url.path}",
        extra={
            "request_id": request_id,
            "validation_errors": [e.model_dump() for e in validation_errors],
        },
    )

    error_response = ValidationErrorResponse(
        error="VALIDATION_ERROR",
        detail="Request validation failed",
        timestamp=datetime.utcnow(),
        request_id=request_id,
        validation_errors=validation_errors,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump(mode="json"),
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Handle standard HTTP exceptions.

    Args:
        request: The FastAPI request object
        exc: The HTTP exception

    Returns:
        JSONResponse with standardized error format
    """
    request_id = get_request_id(request)

    logger.warning(
        f"HTTP {exc.status_code}: {exc.detail}",
        extra={
            "request_id": request_id,
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
        },
    )

    error_response = ErrorResponse(
        error=f"HTTP_{exc.status_code}",
        detail=str(exc.detail),
        timestamp=datetime.utcnow(),
        request_id=request_id,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(mode="json"),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions.

    This is the catch-all handler for any exceptions not caught by other handlers.
    It ensures no internal details are leaked to clients.

    Args:
        request: The FastAPI request object
        exc: The unhandled exception

    Returns:
        JSONResponse with generic error message
    """
    request_id = get_request_id(request)

    # Log full exception details internally
    logger.error(
        f"Unhandled exception: {exc.__class__.__name__}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "exception_type": exc.__class__.__name__,
        },
        exc_info=True,
    )

    # Return generic error to client (don't leak internal details)
    error_response = ErrorResponse(
        error="INTERNAL_SERVER_ERROR",
        detail="An unexpected error occurred. Please try again later.",
        timestamp=datetime.utcnow(),
        request_id=request_id,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(mode="json"),
    )


def register_exception_handlers(app):
    """Register all exception handlers with the FastAPI application.

    Args:
        app: The FastAPI application instance
    """
    # Custom API exceptions
    app.add_exception_handler(APIException, api_exception_handler)
    app.add_exception_handler(ValidationException, api_exception_handler)
    app.add_exception_handler(AuthenticationException, api_exception_handler)
    app.add_exception_handler(AuthorizationException, api_exception_handler)
    app.add_exception_handler(NotFoundException, api_exception_handler)
    app.add_exception_handler(RateLimitException, api_exception_handler)
    app.add_exception_handler(LLMException, api_exception_handler)
    app.add_exception_handler(AgentException, api_exception_handler)
    app.add_exception_handler(TimeoutException, api_exception_handler)

    # Standard FastAPI exceptions
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)

    # Catch-all for unexpected exceptions
    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info("Exception handlers registered successfully")
