from pydantic import BaseModel
from app.common.prompt_config import PromptConfig
from app.common.prompt_loader import load_prompt_config


class ResearchAgentConfig(BaseModel):
    RESEARCH_ANALYZER: PromptConfig

def load_research_agent_config(config_path: str = "research_prompt.yml") -> ResearchAgentConfig:

    config_dict = load_prompt_config(config_path)
    return ResearchAgentConfig(**config_dict)