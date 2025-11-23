from app.config.config import AppConfig
from app.common.logging_config import get_logger
from langchain_openai import ChatOpenAI


logger = get_logger(__name__)


def get_llm(model_name: str, temperature: float = 0) -> ChatOpenAI:
    """
    Create and configure a ChatOpenAI LLM instance.

    Args:
        model_name: The name of the OpenAI model to use
        temperature: Temperature setting for response randomness (0.0 to 2.0)

    Returns:
        Configured ChatOpenAI instance
    """
    logger.debug(f"Creating LLM - Model: {model_name}, Temperature: {temperature}")

    try:
        config = AppConfig()

        # Check if API key is available (without logging the actual key)
        has_api_key = bool(config.openai_api_key)
        logger.debug(f"API key present: {has_api_key}")

        if not has_api_key:
            logger.error("OpenAI API key is missing or empty")
            raise ValueError("OpenAI API key is required but not provided")

        llm_config = {
            "model": model_name,
            "temperature": temperature,
            "openai_api_key": config.openai_api_key
        }

        llm = ChatOpenAI(**llm_config)

        logger.info(f"LLM created successfully - Model: {model_name}")
        return llm

    except Exception as e:
        logger.error(
            f"Failed to create LLM - Model: {model_name}, Error: {str(e)}",
            exc_info=True
        )
        raise