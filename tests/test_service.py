"""Tests for the WeatherService module."""

from unittest.mock import Mock, patch

import pytest
import requests

from weather.service import WeatherService


class TestWeatherService:
    """Test cases for the WeatherService class."""

    def test_init_with_api_key(self):
        """Test WeatherService initialization with API key."""
        service = WeatherService("test_api_key")
        assert service.api_key == "test_api_key"
        assert service.base_url == "https://api.openweathermap.org/data/2.5/weather"

    def test_init_without_api_key(self):
        """Test WeatherService initialization without API key."""
        service = WeatherService()
        assert service.api_key is None
        assert service.base_url == "https://api.openweathermap.org/data/2.5/weather"

    def test_get_weather_raises_value_error_without_api_key(self):
        """Test that get_weather raises ValueError when no API key is set."""
        service = WeatherService()

        with pytest.raises(ValueError) as exc_info:
            service.get_weather("London")

        assert "API key is required" in str(exc_info.value)
        assert "OPENWEATHER_API_KEY" in str(exc_info.value)

    def test_get_weather_raises_value_error_with_empty_api_key(self):
        """Test that get_weather raises ValueError with empty API key."""
        service = WeatherService("")

        with pytest.raises(ValueError) as exc_info:
            service.get_weather("London")

        assert "API key is required" in str(exc_info.value)

    @patch("weather.service.requests.get")
    def test_get_weather_success(self, mock_get):
        """Test successful weather data retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "name": "London",
            "sys": {"country": "GB"},
            "main": {"temp": 20.0, "feels_like": 18.0, "humidity": 65},
            "weather": [{"description": "clear sky"}],
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = WeatherService("test_api_key")
        result = service.get_weather("London")

        expected_params = {
            "q": "London",
            "appid": "test_api_key",
            "units": "metric",
        }
        mock_get.assert_called_once_with(
            "https://api.openweathermap.org/data/2.5/weather",
            params=expected_params,
        )
        mock_response.raise_for_status.assert_called_once()
        assert result == mock_response.json.return_value

    @patch("weather.service.requests.get")
    def test_get_weather_handles_http_error(self, mock_get):
        """Test that get_weather propagates HTTP errors."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        service = WeatherService("test_api_key")

        with pytest.raises(requests.HTTPError):
            service.get_weather("NonexistentCity")

    @patch("weather.service.requests.get")
    def test_get_weather_handles_request_exception(self, mock_get):
        """Test that get_weather propagates request exceptions."""
        mock_get.side_effect = requests.RequestException("Network error")

        service = WeatherService("test_api_key")

        with pytest.raises(requests.RequestException):
            service.get_weather("London")

    @patch("weather.service.requests.get")
    def test_get_weather_with_city_containing_spaces(self, mock_get):
        """Test get_weather with city names containing spaces."""
        mock_response = Mock()
        mock_response.json.return_value = {"name": "New York"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = WeatherService("test_api_key")
        service.get_weather("New York")

        expected_params = {
            "q": "New York",
            "appid": "test_api_key",
            "units": "metric",
        }
        mock_get.assert_called_once_with(
            "https://api.openweathermap.org/data/2.5/weather",
            params=expected_params,
        )

    @patch("weather.service.requests.get")
    def test_get_weather_with_special_characters(self, mock_get):
        """Test get_weather with city names containing special characters."""
        mock_response = Mock()
        mock_response.json.return_value = {"name": "São Paulo"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = WeatherService("test_api_key")
        service.get_weather("São Paulo")

        expected_params = {
            "q": "São Paulo",
            "appid": "test_api_key",
            "units": "metric",
        }
        mock_get.assert_called_once_with(
            "https://api.openweathermap.org/data/2.5/weather",
            params=expected_params,
        )

    def test_format_weather_output_basic(self):
        """Test basic weather data formatting."""
        weather_data = {
            "name": "London",
            "sys": {"country": "GB"},
            "main": {"temp": 20.0, "feels_like": 18.0, "humidity": 65},
            "weather": [{"description": "clear sky"}],
        }

        service = WeatherService("test_api_key")
        result = service.format_weather_output(weather_data)

        expected = """Weather in London, GB:
Temperature: 20.0°C (feels like 18.0°C)
Humidity: 65%
Conditions: Clear Sky"""

        assert result == expected

    def test_format_weather_output_with_integer_values(self):
        """Test weather formatting with integer temperature values."""
        weather_data = {
            "name": "Paris",
            "sys": {"country": "FR"},
            "main": {"temp": 15, "feels_like": 14, "humidity": 70},
            "weather": [{"description": "partly cloudy"}],
        }

        service = WeatherService("test_api_key")
        result = service.format_weather_output(weather_data)

        expected = """Weather in Paris, FR:
Temperature: 15°C (feels like 14°C)
Humidity: 70%
Conditions: Partly Cloudy"""

        assert result == expected

    def test_format_weather_output_with_negative_temperature(self):
        """Test weather formatting with negative temperatures."""
        weather_data = {
            "name": "Moscow",
            "sys": {"country": "RU"},
            "main": {"temp": -5.2, "feels_like": -8.1, "humidity": 85},
            "weather": [{"description": "light snow"}],
        }

        service = WeatherService("test_api_key")
        result = service.format_weather_output(weather_data)

        expected = """Weather in Moscow, RU:
Temperature: -5.2°C (feels like -8.1°C)
Humidity: 85%
Conditions: Light Snow"""

        assert result == expected

    def test_format_weather_output_description_capitalization(self):
        """Test that weather description is properly capitalized."""
        test_cases = [
            ("clear sky", "Clear Sky"),
            ("light rain", "Light Rain"),
            ("heavy thunderstorm", "Heavy Thunderstorm"),
            ("broken clouds", "Broken Clouds"),
        ]

        service = WeatherService("test_api_key")

        for description_input, expected_output in test_cases:
            weather_data = {
                "name": "Test City",
                "sys": {"country": "TC"},
                "main": {"temp": 20.0, "feels_like": 18.0, "humidity": 60},
                "weather": [{"description": description_input}],
            }

            result = service.format_weather_output(weather_data)
            assert expected_output in result

    def test_format_weather_output_missing_keys_raises_error(self):
        """Test that format_weather_output raises KeyError for missing data."""
        incomplete_data = {
            "name": "London",
            "sys": {"country": "GB"},
            # Missing "main" and "weather" keys
        }

        service = WeatherService("test_api_key")

        with pytest.raises(KeyError):
            service.format_weather_output(incomplete_data)

    def test_format_weather_output_missing_nested_keys_raises_error(self):
        """Test format_weather_output with missing nested keys."""
        incomplete_data = {
            "name": "London",
            "sys": {"country": "GB"},
            "main": {"temp": 20.0},  # Missing feels_like and humidity
            "weather": [{"description": "clear sky"}],
        }

        service = WeatherService("test_api_key")

        with pytest.raises(KeyError):
            service.format_weather_output(incomplete_data)

    def test_format_weather_output_empty_weather_array_raises_error(self):
        """Test format_weather_output with empty weather array."""
        weather_data = {
            "name": "London",
            "sys": {"country": "GB"},
            "main": {"temp": 20.0, "feels_like": 18.0, "humidity": 65},
            "weather": [],  # Empty weather array
        }

        service = WeatherService("test_api_key")

        with pytest.raises(IndexError):
            service.format_weather_output(weather_data)

    @patch("weather.service.requests.get")
    def test_get_weather_uses_metric_units(self, mock_get):
        """Test that get_weather always uses metric units."""
        mock_response = Mock()
        mock_response.json.return_value = {"name": "London"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = WeatherService("test_api_key")
        service.get_weather("London")

        # Verify that units=metric is always included in params
        call_args = mock_get.call_args
        assert call_args[1]["params"]["units"] == "metric"

    @patch("weather.service.requests.get")
    def test_get_weather_constructs_correct_url(self, mock_get):
        """Test that get_weather uses the correct API endpoint."""
        mock_response = Mock()
        mock_response.json.return_value = {"name": "London"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = WeatherService("test_api_key")
        service.get_weather("London")

        call_args = mock_get.call_args
        assert call_args[0][0] == "https://api.openweathermap.org/data/2.5/weather"

    def test_api_key_stored_correctly(self):
        """Test that API key is stored correctly during initialization."""
        test_keys = ["abc123", "test_key_with_underscores", "KEY-WITH-DASHES"]

        for key in test_keys:
            service = WeatherService(key)
            assert service.api_key == key

    @patch("weather.service.requests.get")
    def test_integration_full_workflow(self, mock_get):
        """Test complete workflow from API call to formatted output."""
        # Mock API response
        mock_response = Mock()
        api_response = {
            "name": "Tokyo",
            "sys": {"country": "JP"},
            "main": {"temp": 25.5, "feels_like": 27.0, "humidity": 75},
            "weather": [{"description": "few clouds"}],
        }
        mock_response.json.return_value = api_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Test complete workflow
        service = WeatherService("integration_test_key")
        weather_data = service.get_weather("Tokyo")
        formatted_output = service.format_weather_output(weather_data)

        # Verify API was called correctly
        expected_params = {
            "q": "Tokyo",
            "appid": "integration_test_key",
            "units": "metric",
        }
        mock_get.assert_called_once_with(
            "https://api.openweathermap.org/data/2.5/weather",
            params=expected_params,
        )

        # Verify data is returned correctly
        assert weather_data == api_response

        # Verify formatting is correct
        expected_output = """Weather in Tokyo, JP:
Temperature: 25.5°C (feels like 27.0°C)
Humidity: 75%
Conditions: Few Clouds"""
        assert formatted_output == expected_output
