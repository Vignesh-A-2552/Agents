from typing import Any, Dict
import os
import yaml
from app.common.logging_config import get_logger


logger = get_logger(__name__)

def load_prompt_config(config_path: str) -> Dict[str, Any]:
    """
    Load a prompt configuration from a YAML file in the prompts directory.

    Args:
        config_path: Name of the YAML configuration file.

    Returns:
        Dictionary containing the parsed YAML configuration.

    Raises:
        FileNotFoundError: If the configuration file cannot be found.
        yaml.YAMLError: If the YAML file is malformed or cannot be parsed.
    """
    logger.debug(f"Loading prompt config from prompts directory: {config_path}")
    config_path = os.path.join("app/prompts", config_path)
    return load_config(config_path)

def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load the ticket classifier configuration from a YAML file.

    Args:
        config_path: Path to the YAML configuration file.

    Returns:
        Dictionary containing the parsed YAML configuration.

    Raises:
        FileNotFoundError: If the configuration file cannot be found.
        yaml.YAMLError: If the YAML file is malformed or cannot be parsed.
    """
    logger.debug(f"Loading config from path: {config_path}")

    try:
        with open(config_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)

        # Log the keys loaded (without showing sensitive data)
        config_keys = list(config.keys()) if config else []
        logger.info(f"Config loaded successfully - Path: {config_path}, Keys: {config_keys}")

        return config

    except FileNotFoundError:
        logger.error(f"Configuration file not found at: {config_path}")
        raise FileNotFoundError(f"configuration file not found at: {config_path}")

    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML configuration at {config_path}: {str(e)}")
        raise yaml.YAMLError(f"Error parsing YAML configuration: {str(e)}")