"""Tests for the configuration management system."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from weather.config import Config


class TestConfig:
    """Test cases for the Config class."""

    def test_init_with_default_path(self):
        """Test Config initialization with default path."""
        config = Config()
        expected_path = Path.cwd() / "config.yaml"
        assert config.get_config_path() == expected_path

    def test_init_with_custom_path(self):
        """Test Config initialization with custom path."""
        custom_path = Path("/tmp/custom_config.yaml")
        config = Config(custom_path)
        assert config.get_config_path() == custom_path

    def test_load_nonexistent_config_file(self):
        """Test loading when config file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "nonexistent.yaml"
            config = Config(config_path)
            assert not config.has_config_file()
            assert config.get("any.key") is None

    def test_load_valid_yaml_config(self):
        """Test loading a valid YAML config file."""
        config_data = {
            "api": {
                "openweather": {"key": "test_api_key"},
                "other_service": {"key": "other_key"},
            },
            "settings": {"timeout": 30, "retries": 3},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            config_path = Path(f.name)

        try:
            config = Config(config_path)
            assert config.has_config_file()
            assert config.get("api.openweather.key") == "test_api_key"
            assert config.get("settings.timeout") == 30
        finally:
            config_path.unlink()

    def test_load_invalid_yaml_config(self):
        """Test loading an invalid YAML config file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content:\n  - malformed")
            config_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="Error loading config"):
                Config(config_path)
        finally:
            config_path.unlink()

    def test_load_empty_yaml_config(self):
        """Test loading an empty YAML config file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("")
            config_path = Path(f.name)

        try:
            config = Config(config_path)
            assert config.get("any.key") is None
        finally:
            config_path.unlink()

    def test_get_with_simple_key(self):
        """Test get method with simple key."""
        config_data = {"simple_key": "simple_value"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            config_path = Path(f.name)

        try:
            config = Config(config_path)
            assert config.get("simple_key") == "simple_value"
            assert config.get("nonexistent_key") is None
            assert config.get("nonexistent_key", "default") == "default"
        finally:
            config_path.unlink()

    def test_get_with_nested_keys(self):
        """Test get method with nested keys using dot notation."""
        config_data = {
            "level1": {"level2": {"level3": "deep_value"}, "simple": "value"}
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            config_path = Path(f.name)

        try:
            config = Config(config_path)
            assert config.get("level1.level2.level3") == "deep_value"
            assert config.get("level1.simple") == "value"
            assert config.get("level1.nonexistent") is None
            assert config.get("level1.level2.nonexistent", "default") == "default"
        finally:
            config_path.unlink()

    def test_get_with_invalid_path(self):
        """Test get method with invalid nested path."""
        config_data = {"string_value": "not_a_dict"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            config_path = Path(f.name)

        try:
            config = Config(config_path)
            assert config.get("string_value.nested") is None
        finally:
            config_path.unlink()

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "env_api_key"}, clear=False)
    def test_get_api_key_from_environment(self):
        """Test get_api_key returns environment variable when available."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "nonexistent.yaml"
            config = Config(config_path)
            assert config.get_api_key("openweather") == "env_api_key"

    @patch.dict(os.environ, {}, clear=True)
    def test_get_api_key_from_config_file(self):
        """
        Test get_api_key returns value from config file when env var not set.
        """
        config_data = {"api": {"openweather": {"key": "config_api_key"}}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            config_path = Path(f.name)

        try:
            config = Config(config_path)
            assert config.get_api_key("openweather") == "config_api_key"
        finally:
            config_path.unlink()

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "env_api_key"}, clear=False)
    def test_get_api_key_environment_takes_precedence(self):
        """Test that environment variable takes precedence over config file."""
        config_data = {"api": {"openweather": {"key": "config_api_key"}}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            config_path = Path(f.name)

        try:
            config = Config(config_path)
            assert config.get_api_key("openweather") == "env_api_key"
        finally:
            config_path.unlink()

    @patch.dict(os.environ, {}, clear=True)
    def test_get_api_key_not_found(self):
        """Test get_api_key returns None when key not found."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "nonexistent.yaml"
            config = Config(config_path)
            assert config.get_api_key("openweather") is None

    @patch.dict(os.environ, {}, clear=True)
    def test_get_api_key_unknown_service(self):
        """Test get_api_key with unknown service falls back to config file."""
        config_data = {"api": {"unknown_service": {"key": "unknown_api_key"}}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            config_path = Path(f.name)

        try:
            config = Config(config_path)
            assert config.get_api_key("unknown_service") == "unknown_api_key"
        finally:
            config_path.unlink()

    def test_has_config_file_true(self):
        """Test has_config_file returns True when file exists."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump({}, f)
            config_path = Path(f.name)

        try:
            config = Config(config_path)
            assert config.has_config_file() is True
        finally:
            config_path.unlink()

    def test_has_config_file_false(self):
        """Test has_config_file returns False when file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "nonexistent.yaml"
            config = Config(config_path)
            assert config.has_config_file() is False
