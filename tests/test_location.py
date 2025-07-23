"""Tests for the LocationService module."""

from unittest.mock import Mock, patch

import requests

from weather.location import LocationService


class TestLocationService:
    """Test cases for the LocationService class."""

    def test_init(self):
        """Test LocationService initialization."""
        service = LocationService()
        assert service.base_url == "https://ipapi.co/json/"

    @patch("weather.location.LocationService._get_native_location")
    @patch("weather.location.requests.get")
    def test_get_current_location_success_ip_fallback(
        self, mock_get, mock_native
    ):
        """Test successful location retrieval via IP fallback."""
        # Mock native location to return None (fallback to IP)
        mock_native.return_value = None

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
        mock_native.assert_called_once()
        mock_get.assert_called_once_with(
            "https://ipapi.co/json/",
            params={},
            headers={"User-Agent": "weather-cli/1.0"},
            timeout=10,
        )

    @patch("weather.location.LocationService._get_native_location")
    def test_get_current_location_success_native(self, mock_native):
        """Test successful location retrieval via native GPS."""
        mock_native.return_value = (37.7749, -122.4194)  # San Francisco

        service = LocationService()
        result = service.get_current_location()

        assert result == (37.7749, -122.4194)
        mock_native.assert_called_once()

    @patch("weather.location.LocationService._get_native_location")
    @patch("weather.location.requests.get")
    def test_get_current_location_missing_coordinates(
        self, mock_get, mock_native
    ):
        """Test location retrieval with missing coordinates."""
        # Mock native location to return None (fallback to IP)
        mock_native.return_value = None

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

    @patch("weather.location.LocationService._get_native_location")
    @patch("weather.location.requests.get")
    def test_get_current_location_api_error(self, mock_get, mock_native):
        """Test location retrieval with API error response."""
        # Mock native location to return None (fallback to IP)
        mock_native.return_value = None

        mock_response = Mock()
        mock_response.json.return_value = {
            "error": True,
            "reason": "Request rate exceeded",
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = LocationService()
        result = service.get_current_location()

        # Should return None instead of raising error (graceful fallback)
        assert result is None

    @patch("weather.location.LocationService._get_native_location")
    @patch("weather.location.requests.get")
    def test_get_current_location_http_error(self, mock_get, mock_native):
        """Test location retrieval with HTTP error."""
        # Mock native location to return None (fallback to IP)
        mock_native.return_value = None

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError(
            "404 Not Found"
        )
        mock_get.return_value = mock_response

        service = LocationService()
        result = service.get_current_location()

        # Should return None instead of raising error (graceful fallback)
        assert result is None

    @patch("weather.location.LocationService._get_native_location")
    @patch("weather.location.requests.get")
    def test_get_current_location_network_error(self, mock_get, mock_native):
        """Test location retrieval with network error."""
        # Mock native location to return None (fallback to IP)
        mock_native.return_value = None

        mock_get.side_effect = requests.RequestException("Connection error")

        service = LocationService()
        result = service.get_current_location()

        # Should return None instead of raising error (graceful fallback)
        assert result is None

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

    @patch("weather.location.LocationService._get_native_location")
    @patch("weather.location.requests.get")
    def test_get_current_location_coordinate_types(
        self, mock_get, mock_native
    ):
        """Test that coordinates are properly converted to float."""
        # Mock native location to return None (fallback to IP)
        mock_native.return_value = None

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

    @patch("weather.location.LocationService._get_native_location")
    @patch("weather.location.requests.get")
    def test_user_agent_header(self, mock_get, mock_native):
        """Test that proper User-Agent header is sent."""
        # Mock native location to return None (fallback to IP)
        mock_native.return_value = None

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

    @patch("weather.location.LocationService._get_native_location")
    @patch("weather.location.requests.get")
    def test_timeout_configuration(self, mock_get, mock_native):
        """Test that requests have proper timeout."""
        # Mock native location to return None (fallback to IP)
        mock_native.return_value = None

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

    def test_get_native_location_dispatch(self):
        """Test that _get_native_location dispatches to correct platform."""
        service = LocationService()

        with patch("weather.location.sys.platform", "darwin"):
            with patch.object(service, "_get_macos_location") as mock_macos:
                mock_macos.return_value = (37.7749, -122.4194)
                result = service._get_native_location()
                assert result == (37.7749, -122.4194)
                mock_macos.assert_called_once()

        with patch("weather.location.sys.platform", "win32"):
            with patch.object(
                service, "_get_windows_location"
            ) as mock_windows:
                mock_windows.return_value = (40.7128, -74.0060)
                result = service._get_native_location()
                assert result == (40.7128, -74.0060)
                mock_windows.assert_called_once()

        with patch("weather.location.sys.platform", "linux"):
            with patch.object(service, "_get_linux_location") as mock_linux:
                mock_linux.return_value = (51.5074, -0.1278)
                result = service._get_native_location()
                assert result == (51.5074, -0.1278)
                mock_linux.assert_called_once()

    def test_get_native_location_unsupported_platform(self):
        """Test _get_native_location on unsupported platform."""
        service = LocationService()

        with patch("weather.location.sys.platform", "freebsd"):
            result = service._get_native_location()
            assert result is None

    def test_get_native_location_exception_handling(self):
        """Test that _get_native_location handles exceptions gracefully."""
        service = LocationService()

        with patch("weather.location.sys.platform", "darwin"):
            with patch.object(service, "_get_macos_location") as mock_macos:
                mock_macos.side_effect = Exception("GPS error")
                result = service._get_native_location()
                assert result is None
