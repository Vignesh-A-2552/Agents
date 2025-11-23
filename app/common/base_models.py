from typing import Optional
from pydantic import BaseModel, Field


class BaseAgentResponse(BaseModel):
    """Base class for all agent response models."""
    
    processing_summary: Optional[str] = Field(
        default=None, 
        description="Summary of the processing/generation process"
    )

class BaseDocumentResponse(BaseAgentResponse):
    """Base class for agents that generate documents."""
    
    document_title: Optional[str] = Field(
        default=None,
        description="Title for the generated document"
    )