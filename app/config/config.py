import os
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.common.logging_config import get_logger

logger = get_logger(__name__)


class AppConfig(BaseSettings):
    """Application configuration loaded from environment variables.

    This configuration class centralizes all application settings,
    making it easy to manage different environments (dev, staging, prod).
    """

    # Environment
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Application environment (development, staging, production)",
    )

    # Server Configuration
    host: str = Field(
        default="127.0.0.1",
        description="Host to bind the server to (use 0.0.0.0 for production)",
    )
    port: int = Field(
        default=8080,
        ge=1,
        le=65535,
        description="Port to bind the server to",
    )

    # Logging Configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
    )

    # CORS Configuration
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="Comma-separated list of allowed CORS origins",
    )

    # API Keys
    openai_api_key: str = Field(
        ...,
        description="OpenAI API Key for LLM access",
    )

    # Request Configuration
    max_request_size: int = Field(
        default=10_485_760,  # 10MB
        description="Maximum request size in bytes",
    )
    request_timeout: int = Field(
        default=300,
        ge=1,
        description="Request timeout in seconds",
    )
    llm_timeout: int = Field(
        default=120,
        ge=1,
        description="LLM API call timeout in seconds",
    )

    # Input Validation
    max_query_length: int = Field(
        default=10_000,
        ge=1,
        description="Maximum length of user query in characters",
    )
    min_query_length: int = Field(
        default=1,
        ge=1,
        description="Minimum length of user query in characters",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("cors_origins")
    @classmethod
    def validate_cors_origins(cls, v: str) -> str:
        """Validate CORS origins configuration."""
        if v == "*":
            logger.warning(
                "CORS is configured to allow all origins (*). "
                "This is a security risk in production!"
            )
        return v

    @field_validator("host")
    @classmethod
    def validate_host(cls, v: str, info) -> str:
        """Validate host configuration."""
        environment = info.data.get("environment", "development")
        if environment == "production" and v == "127.0.0.1":
            logger.warning(
                "Host is set to 127.0.0.1 in production. "
                "Consider using 0.0.0.0 to accept external connections."
            )
        return v

    def get_cors_origins_list(self) -> list[str]:
        """Parse CORS origins string into a list.

        Returns:
            List of allowed CORS origins
        """
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def is_production(self) -> bool:
        """Check if running in production environment.

        Returns:
            True if environment is production
        """
        return self.environment == "production"

    def is_development(self) -> bool:
        """Check if running in development environment.

        Returns:
            True if environment is development
        """
        return self.environment == "development"

    def __init__(self, **kwargs):
        """Initialize configuration with logging."""
        env_file_path = ".env"
        env_file_exists = os.path.exists(env_file_path)

        logger.debug(f"Loading application configuration - .env file exists: {env_file_exists}")

        try:
            super().__init__(**kwargs)

            # Log configuration (without sensitive values)
            logger.info(
                f"Application configuration loaded - "
                f"Environment: {self.environment}, "
                f"Host: {self.host}, "
                f"Port: {self.port}, "
                f"Log Level: {self.log_level}, "
                f"CORS Origins: {len(self.get_cors_origins_list())} origins, "
                f"OpenAI API key present: {bool(self.openai_api_key)}"
            )

            # Production warnings
            if self.is_production():
                if "*" in self.cors_origins:
                    logger.error("CRITICAL: CORS allows all origins in production!")
                if self.host == "127.0.0.1":
                    logger.warning("WARNING: Host is 127.0.0.1 in production")

        except Exception as e:
            logger.error(f"Failed to load application configuration: {str(e)}", exc_info=True)
            raise