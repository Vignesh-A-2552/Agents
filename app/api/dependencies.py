from dependency_injector.wiring import Provide, inject

from app.agent.research_agent.research_agent import ResearchAgent
from app.container.container import Container

@inject
def get_research_agent(
    research_agent=Provide[Container.research_agent_container],
) -> ResearchAgent:
    """Dependency to get the Research Agent instance."""
    return research_agent