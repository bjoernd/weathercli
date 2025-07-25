"""Tests for the WeatherService module."""

from unittest.mock import Mock, patch

import pytest
import requests

from weather.service import WeatherService
from weather.types import Location


class TestWeatherService:
    """Test cases for the WeatherService class."""

    def test_init_with_api_key(self):
        """Test WeatherService initialization with API key."""
        service = WeatherService("test_api_key")
        assert service.api_key == "test_api_key"
        assert (
            service.base_url
            == "https://api.openweathermap.org/data/2.5/weather"
        )

    def test_init_without_api_key(self):
        """Test WeatherService initialization without API key."""
        service = WeatherService()
        assert service.api_key is None
        assert (
            service.base_url
            == "https://api.openweathermap.org/data/2.5/weather"
        )

    def test_get_weather_raises_value_error_without_api_key(self):
        """Test that get_weather raises ValueError when no API key is set."""
        service = WeatherService()

        with pytest.raises(ValueError) as exc_info:
            service.get_weather(Location.from_city("London"))

        assert "API key is required" in str(exc_info.value)
        assert "OPENWEATHER_API_KEY" in str(exc_info.value)

    def test_get_weather_raises_value_error_with_empty_api_key(self):
        """Test that get_weather raises ValueError with empty API key."""
        service = WeatherService("")

        with pytest.raises(ValueError) as exc_info:
            service.get_weather(Location.from_city("London"))

        assert "API key is required" in str(exc_info.value)

    @patch("weather.base_service.requests.get")
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
        result = service.get_weather(Location.from_city("London"))

        expected_params = {
            "q": "London",
            "appid": "test_api_key",
            "units": "metric",
        }
        mock_get.assert_called_once_with(
            "https://api.openweathermap.org/data/2.5/weather",
            params=expected_params,
            headers={},
            timeout=10,
        )
        mock_response.raise_for_status.assert_called_once()
        assert result == mock_response.json.return_value

    @patch("weather.base_service.requests.get")
    def test_get_weather_handles_http_error(self, mock_get):
        """Test that get_weather propagates HTTP errors."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError(
            "404 Not Found"
        )
        mock_get.return_value = mock_response

        service = WeatherService("test_api_key")

        with pytest.raises(requests.HTTPError):
            service.get_weather(Location.from_city("NonexistentCity"))

    @patch("weather.base_service.requests.get")
    def test_get_weather_handles_request_exception(self, mock_get):
        """Test that get_weather propagates request exceptions."""
        mock_get.side_effect = requests.RequestException("Network error")

        service = WeatherService("test_api_key")

        with pytest.raises(requests.RequestException):
            service.get_weather(Location.from_city("London"))

    @patch("weather.base_service.requests.get")
    def test_get_weather_with_city_containing_spaces(self, mock_get):
        """Test get_weather with city names containing spaces."""
        mock_response = Mock()
        mock_response.json.return_value = {"name": "New York"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = WeatherService("test_api_key")
        service.get_weather(Location.from_city("New York"))

        expected_params = {
            "q": "New York",
            "appid": "test_api_key",
            "units": "metric",
        }
        mock_get.assert_called_once_with(
            "https://api.openweathermap.org/data/2.5/weather",
            params=expected_params,
            headers={},
            timeout=10,
        )

    @patch("weather.base_service.requests.get")
    def test_get_weather_with_special_characters(self, mock_get):
        """Test get_weather with city names containing special characters."""
        mock_response = Mock()
        mock_response.json.return_value = {"name": "São Paulo"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = WeatherService("test_api_key")
        service.get_weather(Location.from_city("São Paulo"))

        expected_params = {
            "q": "São Paulo",
            "appid": "test_api_key",
            "units": "metric",
        }
        mock_get.assert_called_once_with(
            "https://api.openweathermap.org/data/2.5/weather",
            params=expected_params,
            headers={},
            timeout=10,
        )

    def test_format_weather_output_basic(self):
        """Test basic weather data formatting with ASCII art."""
        weather_data = {
            "name": "London",
            "sys": {"country": "GB"},
            "main": {"temp": 20.0, "feels_like": 18.0, "humidity": 65},
            "weather": [{"description": "clear sky", "icon": "01d"}],
        }

        service = WeatherService("test_api_key")
        result = service.format_weather_output(weather_data)

        # Check that result contains both ASCII art and weather text
        assert "Weather in London, GB:" in result
        assert "Temperature: 20.0°C (feels like 18.0°C)" in result
        assert "Humidity: 65%" in result
        assert "Conditions: Clear Sky" in result
        assert "☀️" in result  # Should contain sun emoji from ASCII art

        # Check that result has multiple lines (art + text)
        lines = result.split("\n")
        assert len(lines) >= 4  # Should have at least 4 lines total

    def test_format_weather_output_with_integer_values(self):
        """Test weather formatting with integer temperature values."""
        weather_data = {
            "name": "Paris",
            "sys": {"country": "FR"},
            "main": {"temp": 15, "feels_like": 14, "humidity": 70},
            "weather": [{"description": "partly cloudy", "icon": "02d"}],
        }

        service = WeatherService("test_api_key")
        result = service.format_weather_output(weather_data)

        # Check weather data content
        assert "Weather in Paris, FR:" in result
        assert "Temperature: 15°C (feels like 14°C)" in result
        assert "Humidity: 70%" in result
        assert "Conditions: Partly Cloudy" in result
        # Should contain both sun and cloud emojis for partly cloudy
        assert "☀️" in result or "☁️" in result

    def test_format_weather_output_with_negative_temperature(self):
        """Test weather formatting with negative temperatures."""
        weather_data = {
            "name": "Moscow",
            "sys": {"country": "RU"},
            "main": {"temp": -5.2, "feels_like": -8.1, "humidity": 85},
            "weather": [{"description": "light snow", "icon": "13d"}],
        }

        service = WeatherService("test_api_key")
        result = service.format_weather_output(weather_data)

        # Check weather data content
        assert "Weather in Moscow, RU:" in result
        assert "Temperature: -5.2°C (feels like -8.1°C)" in result
        assert "Humidity: 85%" in result
        assert "Conditions: Light Snow" in result
        assert "❄️" in result  # Should contain snowflake emoji

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
                "weather": [{"description": description_input, "icon": "01d"}],
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
            "weather": [{"description": "clear sky", "icon": "01d"}],
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

    @patch("weather.base_service.requests.get")
    def test_get_weather_uses_metric_units(self, mock_get):
        """Test that get_weather always uses metric units."""
        mock_response = Mock()
        mock_response.json.return_value = {"name": "London"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = WeatherService("test_api_key")
        service.get_weather(Location.from_city("London"))

        # Verify that units=metric is always included in params
        call_args = mock_get.call_args
        assert call_args[1]["params"]["units"] == "metric"

    @patch("weather.base_service.requests.get")
    def test_get_weather_constructs_correct_url(self, mock_get):
        """Test that get_weather uses the correct API endpoint."""
        mock_response = Mock()
        mock_response.json.return_value = {"name": "London"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = WeatherService("test_api_key")
        service.get_weather(Location.from_city("London"))

        call_args = mock_get.call_args
        assert (
            call_args[0][0]
            == "https://api.openweathermap.org/data/2.5/weather"
        )

    def test_api_key_stored_correctly(self):
        """Test that API key is stored correctly during initialization."""
        test_keys = ["abc123", "test_key_with_underscores", "KEY-WITH-DASHES"]

        for key in test_keys:
            service = WeatherService(key)
            assert service.api_key == key

    @patch("weather.base_service.requests.get")
    def test_integration_full_workflow(self, mock_get):
        """Test complete workflow from API call to formatted output."""
        # Mock API response
        mock_response = Mock()
        api_response = {
            "name": "Tokyo",
            "sys": {"country": "JP"},
            "main": {"temp": 25.5, "feels_like": 27.0, "humidity": 75},
            "weather": [{"description": "few clouds", "icon": "02d"}],
        }
        mock_response.json.return_value = api_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Test complete workflow
        service = WeatherService("integration_test_key")
        weather_data = service.get_weather(Location.from_city("Tokyo"))
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
            headers={},
            timeout=10,
        )

        # Verify data is returned correctly
        assert weather_data == api_response

        # Verify formatting includes both ASCII art and weather text
        assert "Weather in Tokyo, JP:" in formatted_output
        assert "Temperature: 25.5°C (feels like 27.0°C)" in formatted_output
        assert "Humidity: 75%" in formatted_output
        assert "Conditions: Few Clouds" in formatted_output
        # Should contain ASCII art elements for few clouds (02d)
        assert "☀️" in formatted_output or "☁️" in formatted_output

    @patch("weather.base_service.requests.get")
    def test_get_weather_with_coordinates(self, mock_get):
        """Test get_weather with latitude and longitude coordinates."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "name": "New York",
            "sys": {"country": "US"},
            "main": {"temp": 22.0, "feels_like": 24.0, "humidity": 55},
            "weather": [{"description": "clear sky"}],
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = WeatherService("test_api_key")
        coordinates = (40.7128, -74.0060)  # New York coordinates
        result = service.get_weather(Location.from_coordinates(*coordinates))

        expected_params = {
            "lat": "40.7128",
            "lon": "-74.006",
            "appid": "test_api_key",
            "units": "metric",
        }
        mock_get.assert_called_once_with(
            "https://api.openweathermap.org/data/2.5/weather",
            params=expected_params,
            headers={},
            timeout=10,
        )
        assert result == mock_response.json.return_value

    @patch("weather.base_service.requests.get")
    def test_get_weather_coordinates_vs_city(self, mock_get):
        """Test that coordinates and city names use different parameters."""
        mock_response = Mock()
        mock_response.json.return_value = {"name": "Test Location"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = WeatherService("test_api_key")

        # Test with city
        service.get_weather(Location.from_city("London"))
        city_call_params = mock_get.call_args[1]["params"]
        assert "q" in city_call_params
        assert "lat" not in city_call_params
        assert "lon" not in city_call_params

        # Reset mock
        mock_get.reset_mock()

        # Test with coordinates
        service.get_weather(Location.from_coordinates(51.5074, -0.1278))
        coord_call_params = mock_get.call_args[1]["params"]
        assert "lat" in coord_call_params
        assert "lon" in coord_call_params
        assert "q" not in coord_call_params

    def test_get_weather_coordinates_type_validation(self):
        """Test that coordinates are properly validated."""
        service = WeatherService("test_api_key")

        # Test with invalid coordinate tuple (wrong length)
        with pytest.raises((ValueError, TypeError)):
            service.get_weather(
                Location.from_coordinates(40.7128)
            )  # Missing longitude

    @patch("weather.base_service.requests.get")
    def test_get_weather_with_negative_coordinates(self, mock_get):
        """Test get_weather with negative coordinates."""
        mock_response = Mock()
        mock_response.json.return_value = {"name": "Southern Hemisphere"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = WeatherService("test_api_key")
        coordinates = (-33.8688, 151.2093)  # Sydney coordinates
        service.get_weather(Location.from_coordinates(*coordinates))

        expected_params = {
            "lat": "-33.8688",
            "lon": "151.2093",
            "appid": "test_api_key",
            "units": "metric",
        }
        mock_get.assert_called_once_with(
            "https://api.openweathermap.org/data/2.5/weather",
            params=expected_params,
            headers={},
            timeout=10,
        )
