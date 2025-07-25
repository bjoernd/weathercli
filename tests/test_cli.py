"""Tests for the CLI module."""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import requests
import yaml
from click.testing import CliRunner

from weather.cli import main
from weather.types import Location


class TestCLI:
    """Test cases for the CLI functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "config.yaml"

    def assert_get_weather_called_with_city(self, mock_service, expected_city):
        """Helper to assert get_weather was called with a Location for city."""
        call_args = mock_service.get_weather.call_args[0][0]
        assert isinstance(call_args, Location)
        assert call_args.city_name == expected_city

    def assert_get_weather_called_with_coords(
        self, mock_service, expected_coords
    ):
        """Helper to assert get_weather called with Location for coords."""
        call_args = mock_service.get_weather.call_args[0][0]
        assert isinstance(call_args, Location)
        assert call_args.is_coordinates
        assert call_args.coordinates == expected_coords

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.config_path.exists():
            self.config_path.unlink()
        Path(self.temp_dir).rmdir()

    @patch("weather.cli.LocationResolver")
    @patch("weather.cli.Config")
    def test_cli_uses_default_city_when_available(
        self, mock_config_class, mock_resolver_class
    ):
        """Test that CLI uses default city when no --city provided and default
        exists."""
        # Setup mock config with default city
        mock_config = Mock()
        mock_config.get_api_key.return_value = None  # API key error
        mock_config_class.return_value = mock_config

        # Setup mock resolver
        mock_resolver = Mock()
        mock_resolver.resolve_location.return_value = Location.from_city(
            "Default City"
        )
        mock_resolver_class.return_value = mock_resolver

        result = self.runner.invoke(main, [])

        # Should exit with API key error, not missing city error
        assert result.exit_code != 0
        assert "Error: OpenWeather API key not found" in result.output
        # Verify the resolver was called correctly
        mock_resolver.resolve_location.assert_called_once_with(False, None)

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
            assert (
                "Environment variable: export OPENWEATHER_API_KEY"
                in result.output
            )
            assert "Config file (config.yaml)" in result.output
            assert "openweathermap.org/api" in result.output

    @patch.dict(
        os.environ, {"OPENWEATHER_API_KEY": "test_env_key"}, clear=False
    )
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
        self.assert_get_weather_called_with_city(mock_service, "London")
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
                "main": {
                    "temp": 15.0,
                    "feels_like": 14.0,
                    "humidity": 70,
                },
                "weather": [{"description": "partly cloudy"}],
            }
            mock_service.get_weather.return_value = mock_weather_data
            mock_service.format_weather_output.return_value = (
                "Weather in Paris"
            )
            mock_weather_service.return_value = mock_service

            result = self.runner.invoke(main, ["--city", "Paris"])

            assert result.exit_code == 0
            mock_weather_service.assert_called_once_with("test_config_key")
            self.assert_get_weather_called_with_city(mock_service, "Paris")
            assert "Weather in Paris" in result.output

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "env_key"}, clear=False)
    @patch("weather.cli.WeatherService")
    def test_environment_takes_precedence_over_config(
        self, mock_weather_service
    ):
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

    @patch.dict(
        os.environ, {"OPENWEATHER_API_KEY": "invalid_key"}, clear=False
    )
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
    def test_handles_requests_exception_other_status(
        self, mock_weather_service
    ):
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
    def test_handles_requests_exception_no_response(
        self, mock_weather_service
    ):
        """Test handling of network errors without response."""
        mock_service = Mock()
        mock_exception = requests.RequestException("Connection error")
        mock_service.get_weather.side_effect = mock_exception
        mock_weather_service.return_value = mock_service

        result = self.runner.invoke(main, ["--city", "London"])

        assert result.exit_code != 0
        assert (
            "Error: Network request failed for London - Connection error"
            in result.output
        )

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
        self.assert_get_weather_called_with_city(mock_service, "New York")
        mock_service.format_weather_output.assert_called_once_with(
            mock_weather_data
        )

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
            # Should still fail due to no API key, but city name should be
            # processed
            assert result.exit_code != 0
            assert "Error: OpenWeather API key not found" in result.output

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_key"}, clear=False)
    @patch("weather.cli.WeatherService")
    def test_weather_service_called_with_correct_city(
        self, mock_weather_service
    ):
        """Test that WeatherService.get_weather is called with correct city."""
        mock_service = Mock()
        mock_service.get_weather.return_value = {}
        mock_service.format_weather_output.return_value = "Weather"
        mock_weather_service.return_value = mock_service

        test_cities = ["London", "New York", "Tokyo", "São Paulo"]

        for city in test_cities:
            result = self.runner.invoke(main, ["--city", city])
            assert result.exit_code == 0

        # Check that get_weather was called with each city as Location objects
        actual_calls = mock_service.get_weather.call_args_list
        assert len(actual_calls) == len(test_cities)

        for i, city in enumerate(test_cities):
            call_args = actual_calls[i].args[0]
            assert isinstance(call_args, Location)
            assert call_args.city_name == city

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_key"}, clear=False)
    @patch("weather.cli.WeatherService")
    @patch("weather.cli.Config")
    def test_uses_default_city_when_no_city_provided(
        self, mock_config_class, mock_weather_service
    ):
        """Test that CLI uses default city when --city is not provided."""
        # Setup mock config
        mock_config = Mock()
        mock_config.get_api_key.return_value = "test_key"
        mock_config.get_default_city.return_value = "Default City"
        mock_config_class.return_value = mock_config

        # Setup mock service
        mock_service = Mock()
        mock_service.get_weather.return_value = {"name": "Default City"}
        mock_service.format_weather_output.return_value = (
            "Weather in Default City"
        )
        mock_weather_service.return_value = mock_service

        result = self.runner.invoke(main, [])

        assert result.exit_code == 0
        assert "Weather in Default City" in result.output
        mock_config.get_default_city.assert_called_once()
        self.assert_get_weather_called_with_city(mock_service, "Default City")

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_key"}, clear=False)
    @patch("weather.cli.LocationResolver")
    @patch("weather.cli.WeatherService")
    @patch("weather.cli.Config")
    def test_auto_location_when_no_city_and_no_default(
        self, mock_config_class, mock_weather_service, mock_location_service
    ):
        """Test automatic location detection when no city and no default."""
        # Setup mock config with no default city
        mock_config = Mock()
        mock_config.get_api_key.return_value = "test_key"
        mock_config.get_default_city.return_value = None
        mock_config_class.return_value = mock_config

        # Setup mock location resolver
        mock_resolver = Mock()
        mock_resolver.resolve_location.return_value = (
            Location.from_coordinates(40.7128, -74.0060)
        )
        mock_location_service.return_value = mock_resolver

        # Setup mock weather service
        mock_service = Mock()
        mock_weather_data = {
            "name": "New York",
            "sys": {"country": "US"},
            "main": {"temp": 20.0, "feels_like": 18.0, "humidity": 65},
            "weather": [{"description": "clear sky"}],
        }
        mock_service.get_weather.return_value = mock_weather_data
        mock_service.format_weather_output.return_value = (
            "Weather in New York, US"
        )
        mock_weather_service.return_value = mock_service

        result = self.runner.invoke(main, [])

        assert result.exit_code == 0
        assert "Weather in New York, US" in result.output
        mock_resolver.resolve_location.assert_called_once_with(False, None)
        self.assert_get_weather_called_with_coords(
            mock_service, (40.7128, -74.0060)
        )

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_key"}, clear=False)
    @patch("weather.cli.LocationResolver")
    @patch("weather.cli.Config")
    def test_auto_location_fails_when_no_city_and_no_default(
        self, mock_config_class, mock_location_service
    ):
        """Test error when automatic location detection fails."""
        # Setup mock config with no default city
        mock_config = Mock()
        mock_config.get_api_key.return_value = "test_key"
        mock_config.get_default_city.return_value = None
        mock_config_class.return_value = mock_config

        # Setup mock location resolver to fail
        mock_resolver = Mock()
        mock_resolver.resolve_location.return_value = None
        mock_location_service.return_value = mock_resolver

        result = self.runner.invoke(main, [])

        assert result.exit_code != 0
        assert "Could not determine location" in result.output
        assert "Use --city 'City Name'" in result.output
        assert "Configure a default city in config.yaml" in result.output

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_key"}, clear=False)
    @patch("weather.cli.LocationResolver")
    @patch("weather.cli.Config")
    def test_auto_location_network_error_when_no_city_and_no_default(
        self, mock_config_class, mock_location_service
    ):
        """Test error when automatic location detection has network error."""
        # Setup mock config with no default city
        mock_config = Mock()
        mock_config.get_api_key.return_value = "test_key"
        mock_config.get_default_city.return_value = None
        mock_config_class.return_value = mock_config

        # Setup mock location resolver to fail (simulating network error)
        mock_resolver = Mock()
        mock_resolver.resolve_location.return_value = None
        mock_location_service.return_value = mock_resolver

        result = self.runner.invoke(main, [])

        assert result.exit_code != 0
        assert "Could not determine location" in result.output
        assert "Use --city 'City Name'" in result.output

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_key"}, clear=False)
    @patch("weather.cli.WeatherService")
    @patch("weather.cli.Config")
    def test_explicit_city_overrides_default(
        self, mock_config_class, mock_weather_service
    ):
        """Test that explicit --city overrides default city."""
        # Setup mock config with default city
        mock_config = Mock()
        mock_config.get_api_key.return_value = "test_key"
        mock_config.get_default_city.return_value = "Default City"
        mock_config_class.return_value = mock_config

        # Setup mock service
        mock_service = Mock()
        mock_service.get_weather.return_value = {"name": "Explicit City"}
        mock_service.format_weather_output.return_value = (
            "Weather in Explicit City"
        )
        mock_weather_service.return_value = mock_service

        result = self.runner.invoke(main, ["--city", "Explicit City"])

        assert result.exit_code == 0
        assert "Weather in Explicit City" in result.output
        # Default city should not be called when explicit city is provided
        mock_config.get_default_city.assert_not_called()
        self.assert_get_weather_called_with_city(mock_service, "Explicit City")

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_key"}, clear=False)
    @patch("weather.cli.LocationResolver")
    @patch("weather.cli.WeatherService")
    def test_current_location_success(
        self, mock_weather_service, mock_location_service
    ):
        """Test successful current location weather retrieval."""
        # Setup mock location resolver
        mock_resolver = Mock()
        mock_resolver.resolve_location.return_value = (
            Location.from_coordinates(40.7128, -74.0060)
        )
        mock_location_service.return_value = mock_resolver

        # Setup mock weather service
        mock_service = Mock()
        mock_weather_data = {
            "name": "New York",
            "sys": {"country": "US"},
            "main": {"temp": 20.0, "feels_like": 18.0, "humidity": 65},
            "weather": [{"description": "clear sky"}],
        }
        mock_service.get_weather.return_value = mock_weather_data
        mock_service.format_weather_output.return_value = (
            "Weather in New York, US"
        )
        mock_weather_service.return_value = mock_service

        result = self.runner.invoke(main, ["--here"])

        assert result.exit_code == 0
        assert "Weather in New York, US" in result.output
        mock_resolver.resolve_location.assert_called_once_with(True, None)
        self.assert_get_weather_called_with_coords(
            mock_service, (40.7128, -74.0060)
        )

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_key"}, clear=False)
    @patch("weather.cli.LocationResolver")
    def test_current_location_fails(self, mock_location_service):
        """Test current location when location service fails."""
        mock_resolver = Mock()
        mock_resolver.resolve_location.return_value = None
        mock_location_service.return_value = mock_resolver

        result = self.runner.invoke(main, ["--here"])

        assert result.exit_code != 0
        assert "Could not determine location" in result.output
        assert "Use --city 'City Name'" in result.output

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_key"}, clear=False)
    @patch("weather.cli.LocationResolver")
    def test_current_location_network_error(self, mock_location_service):
        """Test current location with network error."""
        mock_resolver = Mock()
        mock_resolver.resolve_location.return_value = None
        mock_location_service.return_value = mock_resolver

        result = self.runner.invoke(main, ["--here"])

        assert result.exit_code != 0
        assert "Could not determine location" in result.output

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_key"}, clear=False)
    @patch("weather.cli.LocationResolver")
    @patch("weather.cli.WeatherService")
    def test_current_location_takes_precedence_over_city(
        self, mock_weather_service, mock_location_service
    ):
        """Test that --here takes precedence over --city."""
        # Setup mock location resolver
        mock_resolver = Mock()
        mock_resolver.resolve_location.return_value = (
            Location.from_coordinates(51.5074, -0.1278)
        )
        mock_location_service.return_value = mock_resolver

        # Setup mock weather service
        mock_service = Mock()
        mock_service.get_weather.return_value = {"name": "London"}
        mock_service.format_weather_output.return_value = "Weather in London"
        mock_weather_service.return_value = mock_service

        result = self.runner.invoke(main, ["--here", "--city", "Paris"])

        assert result.exit_code == 0
        # Should use coordinates, not the city name
        self.assert_get_weather_called_with_coords(
            mock_service, (51.5074, -0.1278)
        )

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_key"}, clear=False)
    @patch("weather.cli.LocationResolver")
    @patch("weather.cli.WeatherService")
    def test_current_location_with_weather_api_error(
        self, mock_weather_service, mock_location_service
    ):
        """Test current location with weather API error."""
        # Setup mock location resolver
        mock_resolver = Mock()
        mock_resolver.resolve_location.return_value = (
            Location.from_coordinates(40.7128, -74.0060)
        )
        mock_location_service.return_value = mock_resolver

        # Setup mock weather service to fail
        mock_service = Mock()
        mock_response = Mock()
        mock_response.status_code = 404
        mock_exception = requests.RequestException()
        mock_exception.response = mock_response
        mock_service.get_weather.side_effect = mock_exception
        mock_weather_service.return_value = mock_service

        result = self.runner.invoke(main, ["--here"])

        assert result.exit_code != 0
        assert (
            "No weather data found for coordinates 40.71, -74.01"
            in result.output
        )

    @patch("weather.cli.Config")
    def test_help_message_includes_current_location(self, mock_config_class):
        """Test that help message includes --here option."""
        result = self.runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "--here" in result.output
        assert "Use current location based on IP geolocation" in result.output
