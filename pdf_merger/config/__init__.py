"""
Configuration module.
Handles application configuration management.
"""

# Public API of the config package
from .config_manager import (
    ENV_COLUMN,
    ENV_INPUT_FILE,
    ENV_OUTPUT_DIR,
    ENV_SOURCE_DIR,
    PROJECT_PRESET_FILENAME,
    AppConfig,
    find_project_preset,
    get_config_path,
    load_config,
    load_env_config,
    load_project_preset,
    load_user_config,
    save_config,
)

__all__ = [
    "AppConfig",
    "get_config_path",
    "load_config",
    "save_config",
    "find_project_preset",
    "load_project_preset",
    "load_user_config",
    "load_env_config",
    "ENV_INPUT_FILE",
    "ENV_SOURCE_DIR",
    "ENV_OUTPUT_DIR",
    "ENV_COLUMN",
    "PROJECT_PRESET_FILENAME",
]
