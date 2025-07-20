"""Tests for the CLI module."""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import requests
import yaml
from click.testing import CliRunner

from weather.cli import main


class TestCLI:
    """Test cases for the CLI functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "config.yaml"

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.config_path.exists():
            self.config_path.unlink()
        Path(self.temp_dir).rmdir()

    def test_cli_requires_city_argument(self):
        """Test that CLI requires --city argument."""
        result = self.runner.invoke(main, [])
        assert result.exit_code != 0
        assert "Missing option '--city'" in result.output

    def test_cli_accepts_city_argument(self):
        """Test that CLI accepts --city argument."""
        with patch("weather.cli.Config") as mock_config_class:
            mock_config = Mock()
            mock_config.get_api_key.return_value = None
            mock_config_class.return_value = mock_config

            result = self.runner.invoke(main, ["--city", "London"])
            assert result.exit_code != 0  # Should fail due to no API key
            assert "Error: OpenWeather API key not found" in result.output

    @patch.dict(os.environ, {}, clear=True)
    def test_no_api_key_shows_error_message(self):
        """Test error message when no API key is configured."""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(main, ["--city", "London"])

            assert result.exit_code != 0
            assert "Error: OpenWeather API key not found" in result.output
            assert "Environment variable: export OPENWEATHER_API_KEY" in (
                result.output
            )
            assert "Config file (config.yaml)" in result.output
            assert "openweathermap.org/api" in result.output

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_env_key"}, clear=False)
    @patch("weather.cli.WeatherService")
    def test_uses_environment_api_key(self, mock_weather_service):
        """Test that CLI uses API key from environment variable."""
        mock_service = Mock()
        mock_weather_data = {
            "name": "London",
            "sys": {"country": "GB"},
            "main": {"temp": 20.0, "feels_like": 18.0, "humidity": 65},
            "weather": [{"description": "clear sky"}],
        }
        mock_service.get_weather.return_value = mock_weather_data
        mock_service.format_weather_output.return_value = "Weather in London"
        mock_weather_service.return_value = mock_service

        result = self.runner.invoke(main, ["--city", "London"])

        assert result.exit_code == 0
        mock_weather_service.assert_called_once_with("test_env_key")
        mock_service.get_weather.assert_called_once_with("London")
        assert "Weather in London" in result.output

    @patch.dict(os.environ, {}, clear=True)
    @patch("weather.cli.WeatherService")
    def test_uses_config_file_api_key(self, mock_weather_service):
        """Test that CLI uses API key from config file."""
        config_data = {"api": {"openweather": {"key": "test_config_key"}}}

        with self.runner.isolated_filesystem():
            with open("config.yaml", "w") as f:
                yaml.dump(config_data, f)

            mock_service = Mock()
            mock_weather_data = {
                "name": "Paris",
                "sys": {"country": "FR"},
                "main": {"temp": 15.0, "feels_like": 14.0, "humidity": 70},
                "weather": [{"description": "partly cloudy"}],
            }
            mock_service.get_weather.return_value = mock_weather_data
            mock_service.format_weather_output.return_value = "Weather in Paris"
            mock_weather_service.return_value = mock_service

            result = self.runner.invoke(main, ["--city", "Paris"])

            assert result.exit_code == 0
            mock_weather_service.assert_called_once_with("test_config_key")
            mock_service.get_weather.assert_called_once_with("Paris")
            assert "Weather in Paris" in result.output

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "env_key"}, clear=False)
    @patch("weather.cli.WeatherService")
    def test_environment_takes_precedence_over_config(self, mock_weather_service):
        """Test that environment variable takes precedence over config file."""
        config_data = {"api": {"openweather": {"key": "config_key"}}}

        with self.runner.isolated_filesystem():
            with open("config.yaml", "w") as f:
                yaml.dump(config_data, f)

            mock_service = Mock()
            mock_service.get_weather.return_value = {}
            mock_service.format_weather_output.return_value = "Weather data"
            mock_weather_service.return_value = mock_service

            self.runner.invoke(main, ["--city", "Tokyo"])

            # Should use environment key, not config key
            mock_weather_service.assert_called_once_with("env_key")

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_key"}, clear=False)
    @patch("weather.cli.WeatherService")
    def test_handles_requests_exception_404(self, mock_weather_service):
        """Test handling of 404 error (city not found)."""
        mock_service = Mock()
        mock_response = Mock()
        mock_response.status_code = 404
        mock_exception = requests.RequestException()
        mock_exception.response = mock_response
        mock_service.get_weather.side_effect = mock_exception
        mock_weather_service.return_value = mock_service

        result = self.runner.invoke(main, ["--city", "NonexistentCity"])

        assert result.exit_code != 0
        assert "Error: City 'NonexistentCity' not found" in result.output

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "invalid_key"}, clear=False)
    @patch("weather.cli.WeatherService")
    def test_handles_requests_exception_401(self, mock_weather_service):
        """Test handling of 401 error (invalid API key)."""
        mock_service = Mock()
        mock_response = Mock()
        mock_response.status_code = 401
        mock_exception = requests.RequestException()
        mock_exception.response = mock_response
        mock_service.get_weather.side_effect = mock_exception
        mock_weather_service.return_value = mock_service

        result = self.runner.invoke(main, ["--city", "London"])

        assert result.exit_code != 0
        assert "Error: Invalid API key" in result.output

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_key"}, clear=False)
    @patch("weather.cli.WeatherService")
    def test_handles_requests_exception_other_status(self, mock_weather_service):
        """Test handling of other HTTP errors."""
        mock_service = Mock()
        mock_response = Mock()
        mock_response.status_code = 500
        mock_exception = requests.RequestException()
        mock_exception.response = mock_response
        mock_service.get_weather.side_effect = mock_exception
        mock_weather_service.return_value = mock_service

        result = self.runner.invoke(main, ["--city", "London"])

        assert result.exit_code != 0
        assert "Error: API request failed with status 500" in result.output

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_key"}, clear=False)
    @patch("weather.cli.WeatherService")
    def test_handles_requests_exception_no_response(self, mock_weather_service):
        """Test handling of network errors without response."""
        mock_service = Mock()
        mock_exception = requests.RequestException("Connection error")
        mock_service.get_weather.side_effect = mock_exception
        mock_weather_service.return_value = mock_service

        result = self.runner.invoke(main, ["--city", "London"])

        assert result.exit_code != 0
        assert "Error: Network request failed - Connection error" in result.output

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_key"}, clear=False)
    @patch("weather.cli.WeatherService")
    def test_handles_value_error(self, mock_weather_service):
        """Test handling of ValueError from weather service."""
        mock_service = Mock()
        mock_service.get_weather.side_effect = ValueError("Invalid data")
        mock_weather_service.return_value = mock_service

        result = self.runner.invoke(main, ["--city", "London"])

        assert result.exit_code != 0
        assert "Error: Invalid data" in result.output

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_key"}, clear=False)
    @patch("weather.cli.WeatherService")
    def test_handles_unexpected_exception(self, mock_weather_service):
        """Test handling of unexpected exceptions."""
        mock_service = Mock()
        mock_service.get_weather.side_effect = RuntimeError("Unexpected error")
        mock_weather_service.return_value = mock_service

        result = self.runner.invoke(main, ["--city", "London"])

        assert result.exit_code != 0
        assert "Unexpected error: Unexpected error" in result.output

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_key"}, clear=False)
    @patch("weather.cli.WeatherService")
    def test_successful_weather_display(self, mock_weather_service):
        """Test successful weather data retrieval and display."""
        mock_service = Mock()
        mock_weather_data = {
            "name": "New York",
            "sys": {"country": "US"},
            "main": {"temp": 25.0, "feels_like": 27.0, "humidity": 60},
            "weather": [{"description": "sunny"}],
        }
        expected_output = """Weather in New York, US:
Temperature: 25.0°C (feels like 27.0°C)
Humidity: 60%
Conditions: Sunny"""

        mock_service.get_weather.return_value = mock_weather_data
        mock_service.format_weather_output.return_value = expected_output
        mock_weather_service.return_value = mock_service

        result = self.runner.invoke(main, ["--city", "New York"])

        assert result.exit_code == 0
        assert expected_output in result.output
        mock_service.get_weather.assert_called_once_with("New York")
        mock_service.format_weather_output.assert_called_once_with(mock_weather_data)

    @patch("weather.cli.Config")
    def test_config_initialization(self, mock_config_class):
        """Test that Config is properly initialized."""
        mock_config = Mock()
        mock_config.get_api_key.return_value = None
        mock_config_class.return_value = mock_config

        self.runner.invoke(main, ["--city", "London"])

        # Config should be initialized with no arguments (uses default path)
        mock_config_class.assert_called_once_with()
        mock_config.get_api_key.assert_called_once_with("openweather")

    def test_city_argument_with_spaces(self):
        """Test that city names with spaces are handled correctly."""
        with patch("weather.cli.Config") as mock_config_class:
            mock_config = Mock()
            mock_config.get_api_key.return_value = None
            mock_config_class.return_value = mock_config

            result = self.runner.invoke(main, ["--city", "New York"])
            # Should still fail due to no API key, but city name should be processed
            assert result.exit_code != 0
            assert "Error: OpenWeather API key not found" in result.output

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_key"}, clear=False)
    @patch("weather.cli.WeatherService")
    def test_weather_service_called_with_correct_city(self, mock_weather_service):
        """Test that WeatherService.get_weather is called with correct city."""
        mock_service = Mock()
        mock_service.get_weather.return_value = {}
        mock_service.format_weather_output.return_value = "Weather"
        mock_weather_service.return_value = mock_service

        test_cities = ["London", "New York", "Tokyo", "São Paulo"]

        for city in test_cities:
            result = self.runner.invoke(main, ["--city", city])
            assert result.exit_code == 0

        # Check that get_weather was called with each city
        expected_calls = [(city,) for city in test_cities]
        actual_calls = [call.args for call in mock_service.get_weather.call_args_list]
        assert actual_calls == expected_calls
