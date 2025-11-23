from typing import Optional
from pydantic import BaseModel


class PromptConfig(BaseModel):
    """Configuration for a specific prompt version."""

    model: str
    temperature: float = 0.0
    prompt: Optional[str] = (
        None  # legacy field, use system_prompt and user_prompt_template instead
    )
    system_prompt: Optional[str] = None
    user_prompt_template: Optional[str] = None
