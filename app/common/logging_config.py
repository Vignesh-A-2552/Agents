"""
Central logging configuration module for the application.

This module provides:
- Console-only logging output
- Human-readable log format with timestamps
- Configurable log level via environment variables
- Helper function to get configured loggers
"""

import logging
from typing import Optional

# Log format
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Track if logging has been initialized
_initialized = False


class AppOnlyFilter(logging.Filter):
    """
    Filter that only allows logs from the app module to pass through.

    This reduces noise from third-party libraries in console output.
    """

    def filter(self, record):
        # Only show logs from 'app' or '__main__' (our application)
        return record.name.startswith("app") or record.name == "__main__"


def setup_logging(log_level: Optional[str] = None):
    """
    Initialize the logging system with console output only.

    This should be called once at application startup.

    Args:
        log_level: Logging level as string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
                   If not provided, defaults to INFO.
    """
    global _initialized

    if _initialized:
        return

    # Parse log level
    if log_level:
        level = getattr(logging, log_level.upper(), logging.INFO)
    else:
        level = logging.INFO

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # Add app-only filter to console handler (reduce noise from third-party libs)
    app_filter = AppOnlyFilter()
    console_handler.addFilter(app_filter)

    # Set formatter to handler
    console_handler.setFormatter(formatter)

    # Add handler to root logger
    root_logger.addHandler(console_handler)

    _initialized = True

    # Log initialization
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized - Level: {logging.getLevelName(level)}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (typically __name__ of the calling module)

    Returns:
        Configured logger instance
    """
    if not _initialized:
        setup_logging()

    return logging.getLogger(name)


def set_log_level(level: int):
    """
    Change the log level dynamically.

    Args:
        level: Logging level (e.g., logging.DEBUG, logging.INFO)
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Update all handlers
    for handler in root_logger.handlers:
        handler.setLevel(level)

    logger = logging.getLogger(__name__)
    logger.info(f"Log level changed to {logging.getLevelName(level)}")
