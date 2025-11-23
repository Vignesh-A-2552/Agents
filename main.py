import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.exception_handlers import register_exception_handlers
from app.common.logging_config import get_logger, setup_logging
from app.config.config import AppConfig
from app.container.container import Container

# Initialize configuration first
config = AppConfig()

# Initialize logging with config
setup_logging(log_level=config.log_level)
logger = get_logger(__name__)

logger.info(f"Starting Agents Backend - Environment: {config.environment}")

# Initialize the dependency injection container
logger.info("Initializing dependency injection container")
container = Container()

container.init_resources()
container.wire(
    modules=[
        __name__,
        "app.api.dependencies",  # Wire to dependencies module only
    ]
)
logger.info("Container wired successfully")

# Import routers AFTER wiring
from app.api.router.chat import router as chat_router

logger.info("Creating FastAPI application")
app = FastAPI(
    title="Agents Backend API",
    description=(
        "AI-powered research agent API built with FastAPI and LangChain. "
        "This API provides endpoints for research queries with both synchronous "
        "and streaming response modes."
    ),
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Store container and config in app state for lifecycle management
app.state.container = container
app.state.config = config

# Add CORS middleware with configuration
cors_origins = config.get_cors_origins_list()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True if "*" not in cors_origins else False,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info(f"CORS middleware configured - Origins: {cors_origins}")

# Register exception handlers
register_exception_handlers(app)

# Include routers
app.include_router(chat_router, tags=["Chat"])
logger.info("Chat router registered")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Agents Backend API",
        "version": "1.0.0",
        "status": "operational",
        "environment": config.environment,
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring and container orchestration.

    Returns:
        dict: Health status information
    """
    return {
        "status": "healthy",
        "environment": config.environment,
        "version": "1.0.0",
    }


if __name__ == "__main__":
    logger.info(f"Starting application server on http://{config.host}:{config.port}")
    logger.info(f"API Documentation available at: http://{config.host}:{config.port}/docs")
    uvicorn.run(
        app,
        host=config.host,
        port=config.port,
        log_level=config.log_level.lower(),
    )
