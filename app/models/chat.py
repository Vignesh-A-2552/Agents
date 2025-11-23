from pydantic import BaseModel

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    query: str


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    research_summary: str
    research_documents: str