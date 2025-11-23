"""Custom exception classes for the Agents API.

This module defines application-specific exceptions with proper HTTP status codes
and error details for consistent error handling across the API.
"""

from typing import Any, Optional


class APIException(Exception):
    """Base exception class for all API errors.

    Attributes:
        status_code: HTTP status code for the error
        detail: Human-readable error message
        error_code: Machine-readable error code
        extra: Additional error context
    """

    def __init__(
        self,
        detail: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        extra: Optional[dict[str, Any]] = None,
    ):
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.extra = extra or {}
        super().__init__(self.detail)


class ValidationException(APIException):
    """Exception for request validation errors (400 Bad Request)."""

    def __init__(
        self,
        detail: str,
        error_code: str = "VALIDATION_ERROR",
        extra: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            detail=detail,
            status_code=400,
            error_code=error_code,
            extra=extra,
        )


class AuthenticationException(APIException):
    """Exception for authentication errors (401 Unauthorized)."""

    def __init__(
        self,
        detail: str = "Authentication required",
        error_code: str = "AUTHENTICATION_REQUIRED",
        extra: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            detail=detail,
            status_code=401,
            error_code=error_code,
            extra=extra,
        )


class AuthorizationException(APIException):
    """Exception for authorization errors (403 Forbidden)."""

    def __init__(
        self,
        detail: str = "Insufficient permissions",
        error_code: str = "FORBIDDEN",
        extra: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            detail=detail,
            status_code=403,
            error_code=error_code,
            extra=extra,
        )


class NotFoundException(APIException):
    """Exception for resource not found errors (404 Not Found)."""

    def __init__(
        self,
        detail: str = "Resource not found",
        error_code: str = "NOT_FOUND",
        extra: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            detail=detail,
            status_code=404,
            error_code=error_code,
            extra=extra,
        )


class RateLimitException(APIException):
    """Exception for rate limit exceeded errors (429 Too Many Requests)."""

    def __init__(
        self,
        detail: str = "Rate limit exceeded",
        error_code: str = "RATE_LIMIT_EXCEEDED",
        extra: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            detail=detail,
            status_code=429,
            error_code=error_code,
            extra=extra,
        )


class LLMException(APIException):
    """Exception for LLM-related errors (502 Bad Gateway or 500)."""

    def __init__(
        self,
        detail: str,
        status_code: int = 502,
        error_code: str = "LLM_ERROR",
        extra: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            detail=detail,
            status_code=status_code,
            error_code=error_code,
            extra=extra,
        )


class AgentException(APIException):
    """Exception for agent execution errors (500 Internal Server Error)."""

    def __init__(
        self,
        detail: str,
        error_code: str = "AGENT_ERROR",
        extra: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            detail=detail,
            status_code=500,
            error_code=error_code,
            extra=extra,
        )


class TimeoutException(APIException):
    """Exception for request timeout errors (504 Gateway Timeout)."""

    def __init__(
        self,
        detail: str = "Request timeout",
        error_code: str = "TIMEOUT",
        extra: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            detail=detail,
            status_code=504,
            error_code=error_code,
            extra=extra,
        )
