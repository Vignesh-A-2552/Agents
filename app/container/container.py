from dependency_injector import containers, providers
from app.agent.research_agent.research_agent import ResearchAgent
from app.common.logging_config import get_logger


logger = get_logger(__name__)


class Container(containers.DeclarativeContainer):
    """Dependency injection container for the application."""

    research_agent_container = providers.Singleton(
        ResearchAgent
    )

    def __init__(self, *args, **kwargs):
        """Initialize the container with logging."""
        logger.debug("Initializing dependency injection container")
        super().__init__(*args, **kwargs)
        logger.debug("Container initialized")

    def init_resources(self):
        """Initialize container resources with logging."""
        logger.debug("Initializing container resources")
        super().init_resources()
        logger.info("Container resources initialized - Providers: ResearchAgent (Singleton)")

    def wire(self, modules=None, packages=None, **kwargs):
        """Wire the container to modules with logging."""
        logger.debug(f"Wiring container - Modules: {modules}, Packages: {packages}")
        super().wire(modules=modules, packages=packages, **kwargs)
        logger.info(f"Container wired successfully - Modules: {modules}")