"""Configuration management for the weather application."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from weather.constants import (DEFAULT_CITY_CONFIG_KEY,
                               OPENWEATHER_API_KEY_ENV, OPENWEATHER_CONFIG_KEY)
from weather.logging_config import get_logger, timer


class Config:
    """Handles loading and accessing configuration from YAML files."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize config with optional custom path.

        Args:
            config_path: Custom path to config file. Defaults to config.yaml
                        in current directory.
        """
        self.logger = get_logger(__name__)

        if config_path is None:
            config_path = Path.cwd() / "config.yaml"

        self.config_path = config_path
        self._config_data: Dict[str, Any] = {}

        with timer(self.logger, "config file loading"):
            self._load_config()

    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            self._config_data = {}
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as file:
                self._config_data = yaml.safe_load(file) or {}
        except (yaml.YAMLError, IOError) as e:
            raise ValueError(
                f"Error loading config from {self.config_path}: {e}"
            )

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.

        Supports nested keys using dot notation (e.g., 'api.weather.key').

        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split(".")
        value = self._config_data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_api_key(self, service: str = "openweather") -> Optional[str]:
        """
        Get API key for a specific service.

        First checks environment variables, then config file.

        Args:
            service: Service name (e.g., 'openweather')

        Returns:
            API key if found, None otherwise
        """
        if service == "openweather":
            env_value = os.getenv(OPENWEATHER_API_KEY_ENV)
            if env_value:
                return env_value
            return self.get(OPENWEATHER_CONFIG_KEY)

        # For unknown services, check config file pattern
        config_key = f"api.{service}.key"
        return self.get(config_key)

    def get_default_city(self) -> Optional[str]:
        """
        Get the default city from configuration.

        Returns:
            Default city if configured, None otherwise
        """
        return self.get(DEFAULT_CITY_CONFIG_KEY)

    def has_config_file(self) -> bool:
        """Check if config file exists."""
        return self.config_path.exists()

    def get_config_path(self) -> Path:
        """Get the path to the config file."""
        return self.config_path
