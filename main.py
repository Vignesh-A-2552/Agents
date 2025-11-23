from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from app.container.container import Container
from app.common.logging_config import setup_logging, get_logger

# Initialize logging first
setup_logging()
logger = get_logger(__name__)


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
app = FastAPI()

# Store container in app state for lifecycle management
app.state.container = container

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("CORS middleware configured - Origins: ['*']")

# Include routers
app.include_router(chat_router)
logger.info("Chat router registered")


if __name__ == "__main__":
    logger.info("Starting application server on http://127.0.0.1:8080")
    uvicorn.run(app, host="127.0.0.1", port=8080)
