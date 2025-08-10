"""Configuration module for LlamaAgent.

Author: Nik Jois <nikjois@llamasearch.ai>
"""

import os
from typing import Any

from .settings import get_settings, APIConfig, SecurityConfig  # re-export


class ConfigManager:
    """Basic configuration manager."""

    def __init__(self) -> None:
        self.config: dict[str, Any] = {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value


def get_config(key: str, default: Any = None) -> Any:
    """Convenience accessor used in tests.

    Loads from environment variables first, then in-memory defaults.
    """
    env_key = key.upper().replace(".", "_")
    if env_key in os.environ:
        return os.environ[env_key]
    return ConfigManager().get(key, default)


def get_api_config() -> APIConfig:
    """Return API server configuration from global settings."""
    return get_settings().api


def get_security_config() -> SecurityConfig:
    """Return security configuration from global settings."""
    return get_settings().security


__all__ = [
    "ConfigManager",
    "get_config",
    "get_settings",
    "get_api_config",
    "get_security_config",
    "APIConfig",
    "SecurityConfig",
]
