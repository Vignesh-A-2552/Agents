"""Error response models for the Agents API.

This module defines Pydantic models for standardized error responses
returned by the API endpoints.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response model.

    Used for all API error responses to ensure consistency.
    """

    error: str = Field(
        ...,
        description="Machine-readable error code (e.g., VALIDATION_ERROR, AGENT_ERROR)",
        examples=["VALIDATION_ERROR", "AGENT_ERROR", "LLM_ERROR"],
    )
    detail: str = Field(
        ...,
        description="Human-readable error message describing what went wrong",
        examples=["Query must be between 1 and 10000 characters"],
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="ISO 8601 timestamp when the error occurred",
    )
    request_id: Optional[str] = Field(
        None,
        description="Unique identifier for the request (for debugging and support)",
    )
    extra: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context-specific error information",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "error": "VALIDATION_ERROR",
                "detail": "Query must be between 1 and 10000 characters",
                "timestamp": "2024-01-15T10:30:00Z",
                "request_id": "req_abc123xyz",
                "extra": {"field": "query", "max_length": 10000},
            }
        }


class ValidationErrorDetail(BaseModel):
    """Detailed validation error for a specific field."""

    field: str = Field(..., description="The field that failed validation")
    message: str = Field(..., description="Validation error message")
    type: str = Field(..., description="Type of validation error")


class ValidationErrorResponse(BaseModel):
    """Enhanced error response for validation errors (422).

    Provides detailed field-level validation errors.
    """

    error: str = Field(
        default="VALIDATION_ERROR",
        description="Error code",
    )
    detail: str = Field(
        ...,
        description="Summary of validation errors",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="ISO 8601 timestamp when the error occurred",
    )
    request_id: Optional[str] = Field(
        None,
        description="Unique identifier for the request",
    )
    validation_errors: list[ValidationErrorDetail] = Field(
        default_factory=list,
        description="Detailed validation errors per field",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "error": "VALIDATION_ERROR",
                "detail": "Request validation failed",
                "timestamp": "2024-01-15T10:30:00Z",
                "request_id": "req_abc123xyz",
                "validation_errors": [
                    {
                        "field": "query",
                        "message": "String should have at most 10000 characters",
                        "type": "string_too_long",
                    }
                ],
            }
        }
