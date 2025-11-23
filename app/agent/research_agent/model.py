"""Pydantic models for SRS Agent"""

from pydantic import Field
from app.common.base_models import BaseDocumentResponse


class ResearchGenerationResponse(BaseDocumentResponse):
    """LLM structured output for SRS document generation."""

    research_document: str = Field(description="Generated Software Requirements Specification document")