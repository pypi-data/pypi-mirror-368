import os
import warnings
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml
from dotenv import load_dotenv


def get_default_config_path() -> Path:
    """
    Get the default configuration file path.

    Returns:
        Path to the default api.yaml file
    """
    # Try to find api.yaml in current working directory first
    cwd_config = Path.cwd() / "api.yaml"
    if cwd_config.exists():
        return cwd_config

    # Try to find api.yaml in user's home directory
    home_config = Path.home() / ".langchain-llm-config" / "api.yaml"
    if home_config.exists():
        return home_config

    # Return the current working directory as default location
    return cwd_config


def _get_default_api_key(env_var: str) -> str:
    """Get default API key for common environment variables."""
    default_values = {
        "OPENAI_API_KEY": "sk-demo-key-not-for-production",
        "GEMINI_API_KEY": "demo-key-not-for-production",
        "ANTHROPIC_API_KEY": "sk-ant-demo-key-not-for-production",
    }
    return default_values.get(env_var, "")


def _process_environment_variable(
    env_var: str,
    env_value: Optional[str],
    strict: bool,
    service_config: Dict[str, Any],
    key: str,
) -> None:
    """Process a single environment variable."""
    if env_value is None:
        if strict:
            raise ValueError(f"Environment variable {env_var} not set")
        else:
            default_value = _get_default_api_key(env_var)
            service_config[key] = default_value
            warnings.warn(
                f"Environment variable {env_var} not set. Using "
                f"default value. Set {env_var} in your environment "
                f"or .env file for production use.",
                UserWarning,
                stacklevel=2,
            )
    else:
        service_config[key] = env_value


def load_config(
    config_path: Optional[Union[str, Path]] = None, strict: bool = False
) -> Dict[str, Any]:
    """
    Load LLM configuration

    Args:
        config_path: Configuration file path, defaults to api.yaml in current directory
        strict: If True, raise ValueError for missing environment variables.
                If False, use default values and show warnings.

    Returns:
        Processed configuration dictionary

    Raises:
        ValueError: Configuration file not found or environment variables not
                   set (if strict=True)
    """
    # Load environment variables from .env file
    dotenv_path = Path.cwd() / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path)

    if config_path is None:
        config_path = get_default_config_path()
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        raise ValueError(f"Configuration file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config: Dict[str, Any] = yaml.safe_load(f)

    # Process environment variables
    llm_config: Dict[str, Any] = config["llm"]
    for provider_name, provider_config in llm_config.items():
        if provider_name == "default":
            continue

        for service_type, service_config in provider_config.items():
            for key, value in service_config.items():
                if (
                    isinstance(value, str)
                    and value.startswith("${")
                    and value.endswith("}")
                ):
                    env_var = value[2:-1]
                    env_value = os.getenv(env_var)
                    _process_environment_variable(
                        env_var, env_value, strict, service_config, key
                    )

    return llm_config


def init_config(config_path: Optional[Union[str, Path]] = None) -> Path:
    """
    Initialize a new configuration file with default settings.

    Args:
        config_path: Path where to create the configuration file

    Returns:
        Path to the created configuration file
    """
    if config_path is None:
        config_path = get_default_config_path()
    else:
        config_path = Path(config_path)

    # Create parent directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Get the template configuration
    template_path = Path(__file__).parent / "templates" / "api.yaml"

    if template_path.exists():
        # Copy template to target location
        import shutil

        shutil.copy2(template_path, config_path)
    else:
        # If template doesn't exist, create a minimal configuration
        # This should rarely happen since we include the template in the package
        minimal_config: Dict[str, Any] = {
            "llm": {
                "default": {"chat_provider": "openai", "embedding_provider": "openai"},
                "openai": {
                    "chat": {
                        "api_key": "${OPENAI_API_KEY}",
                        "model_name": "gpt-3.5-turbo",
                    },
                    "embeddings": {
                        "api_key": "${OPENAI_API_KEY}",
                        "model_name": "text-embedding-ada-002",
                    },
                },
            }
        }

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(minimal_config, f, default_flow_style=False, allow_unicode=True)

    return config_path
