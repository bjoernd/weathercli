"""Location service for getting current location via IP geolocation."""

from typing import Dict, Optional, Tuple

import requests

from weather.base_service import BaseAPIService
from weather.constants import IPAPI_BASE_URL, USER_AGENT


class LocationService(BaseAPIService):
    """Service for getting current location via IP geolocation."""

    def __init__(self):
        """Initialize location service."""
        super().__init__(IPAPI_BASE_URL)

    def get_current_location(self) -> Optional[Tuple[float, float]]:
        """
        Get current location coordinates via IP geolocation.

        Returns:
            Tuple of (latitude, longitude) or None if failed

        Raises:
            requests.RequestException: If API request fails
        """
        location_data = self._make_request(
            headers={"User-Agent": USER_AGENT}
        )

        if location_data.get("error"):
            error_msg = location_data.get("reason", "Unknown error")
            raise ValueError(f"Location service error: {error_msg}")

        latitude = location_data.get("latitude")
        longitude = location_data.get("longitude")

        if latitude is None or longitude is None:
            return None

        return (float(latitude), float(longitude))

    def get_location_info(self) -> Optional[Dict[str, str]]:
        """
        Get detailed location information via IP geolocation.

        Returns:
            Dictionary containing location details or None if failed
        """
        try:
            location_data = self._make_request(
                headers={"User-Agent": USER_AGENT}
            )

            if location_data.get("error"):
                return None

            return {
                "city": location_data.get("city", "Unknown"),
                "region": location_data.get("region", "Unknown"),
                "country": location_data.get("country_name", "Unknown"),
                "country_code": location_data.get("country", "Unknown"),
                "timezone": location_data.get("timezone", "Unknown"),
            }
        except (requests.RequestException, ValueError, KeyError):
            return None
