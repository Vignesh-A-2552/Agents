from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from app.common.logging_config import get_logger
import os


logger = get_logger(__name__)


class AppConfig(BaseSettings):
    """Application configuration loaded from environment variables."""

    openai_api_key: str = Field(..., description="OpenAI API Key")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    def __init__(self, **kwargs):
        """Initialize configuration with logging."""
        env_file_path = ".env"
        env_file_exists = os.path.exists(env_file_path)

        logger.debug(f"Loading application configuration - .env file exists: {env_file_exists}")

        try:
            super().__init__(**kwargs)

            # Log that config was loaded successfully (without showing sensitive values)
            has_api_key = bool(self.openai_api_key)
            logger.info(
                f"Application configuration loaded - "
                f"OpenAI API key present: {has_api_key}"
            )

        except Exception as e:
            logger.error(f"Failed to load application configuration: {str(e)}", exc_info=True)
            raise