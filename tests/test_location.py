"""Tests for the LocationService module."""

from unittest.mock import Mock, patch

import pytest
import requests

from weather.location import LocationService


class TestLocationService:
    """Test cases for the LocationService class."""

    def test_init(self):
        """Test LocationService initialization."""
        service = LocationService()
        assert service.base_url == "https://ipapi.co/json/"

    @patch("weather.location.requests.get")
    def test_get_current_location_success(self, mock_get):
        """Test successful location retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "city": "New York",
            "country": "US",
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = LocationService()
        result = service.get_current_location()

        assert result == (40.7128, -74.0060)
        mock_get.assert_called_once_with(
            "https://ipapi.co/json/",
            headers={"User-Agent": "weather-cli/1.0"},
            timeout=10,
        )

    @patch("weather.location.requests.get")
    def test_get_current_location_missing_coordinates(self, mock_get):
        """Test location retrieval with missing coordinates."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "city": "New York",
            "country": "US",
            # Missing latitude and longitude
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = LocationService()
        result = service.get_current_location()

        assert result is None

    @patch("weather.location.requests.get")
    def test_get_current_location_api_error(self, mock_get):
        """Test location retrieval with API error response."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "error": True,
            "reason": "Request rate exceeded",
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = LocationService()

        with pytest.raises(ValueError, match="Location service error"):
            service.get_current_location()

    @patch("weather.location.requests.get")
    def test_get_current_location_http_error(self, mock_get):
        """Test location retrieval with HTTP error."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError(
            "404 Not Found"
        )
        mock_get.return_value = mock_response

        service = LocationService()

        with pytest.raises(requests.HTTPError):
            service.get_current_location()

    @patch("weather.location.requests.get")
    def test_get_current_location_network_error(self, mock_get):
        """Test location retrieval with network error."""
        mock_get.side_effect = requests.RequestException("Connection error")

        service = LocationService()

        with pytest.raises(requests.RequestException):
            service.get_current_location()

    @patch("weather.location.requests.get")
    def test_get_location_info_success(self, mock_get):
        """Test successful detailed location info retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "city": "New York",
            "region": "New York",
            "country_name": "United States",
            "country": "US",
            "timezone": "America/New_York",
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = LocationService()
        result = service.get_location_info()

        expected = {
            "city": "New York",
            "region": "New York",
            "country": "United States",
            "country_code": "US",
            "timezone": "America/New_York",
        }
        assert result == expected

    @patch("weather.location.requests.get")
    def test_get_location_info_partial_data(self, mock_get):
        """Test location info with partial data."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "city": "London",
            "country": "GB",
            # Missing other fields
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = LocationService()
        result = service.get_location_info()

        expected = {
            "city": "London",
            "region": "Unknown",
            "country": "Unknown",
            "country_code": "GB",
            "timezone": "Unknown",
        }
        assert result == expected

    @patch("weather.location.requests.get")
    def test_get_location_info_api_error(self, mock_get):
        """Test location info with API error."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "error": True,
            "reason": "Invalid request",
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = LocationService()
        result = service.get_location_info()

        assert result is None

    @patch("weather.location.requests.get")
    def test_get_location_info_network_error(self, mock_get):
        """Test location info with network error."""
        mock_get.side_effect = requests.RequestException("Connection error")

        service = LocationService()
        result = service.get_location_info()

        assert result is None

    @patch("weather.location.requests.get")
    def test_get_current_location_coordinate_types(self, mock_get):
        """Test that coordinates are properly converted to float."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "latitude": "40.7128",  # String instead of float
            "longitude": "-74.0060",  # String instead of float
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = LocationService()
        result = service.get_current_location()

        # Should convert strings to floats
        assert result == (40.7128, -74.0060)
        assert isinstance(result[0], float)
        assert isinstance(result[1], float)

    @patch("weather.location.requests.get")
    def test_user_agent_header(self, mock_get):
        """Test that proper User-Agent header is sent."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "latitude": 40.7128,
            "longitude": -74.0060,
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = LocationService()
        service.get_current_location()

        # Verify User-Agent header was sent
        call_args = mock_get.call_args
        headers = call_args[1]["headers"]
        assert headers["User-Agent"] == "weather-cli/1.0"

    @patch("weather.location.requests.get")
    def test_timeout_configuration(self, mock_get):
        """Test that requests have proper timeout."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "latitude": 40.7128,
            "longitude": -74.0060,
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = LocationService()
        service.get_current_location()

        # Verify timeout was set
        call_args = mock_get.call_args
        timeout = call_args[1]["timeout"]
        assert timeout == 10
