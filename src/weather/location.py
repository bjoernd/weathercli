"""Location service for getting current location via IP geolocation."""

from typing import Dict, Optional, Tuple

import requests

from weather.logging_config import get_logger, timer


class LocationService:
    """Service for getting current location via IP geolocation."""

    def __init__(self):
        """Initialize location service."""
        self.base_url = "https://ipapi.co/json/"
        self.logger = get_logger(__name__)
        self.logger.debug("LocationService initialized")

    def get_current_location(self) -> Optional[Tuple[float, float]]:
        """
        Get current location coordinates via IP geolocation.

        Returns:
            Tuple of (latitude, longitude) or None if failed

        Raises:
            requests.RequestException: If API request fails
        """
        self.logger.debug("Getting current location via IP geolocation")

        with timer(self.logger, f"IP geolocation request to {self.base_url}"):
            self.logger.debug(f"Making request to: {self.base_url}")
            response = requests.get(
                self.base_url,
                headers={"User-Agent": "weather-cli/1.0"},
                timeout=10,
            )
            self.logger.debug(f"Response status: {response.status_code}")

            response.raise_for_status()

        with timer(self.logger, "location data parsing"):
            location_data = response.json()
            self.logger.debug(f"Location data received: {location_data}")

            # Check for error in response
            if location_data.get("error"):
                error_msg = location_data.get("reason", "Unknown error")
                self.logger.debug(f"API returned error: {error_msg}")
                raise ValueError(f"Location service error: {error_msg}")

            # Extract coordinates
            latitude = location_data.get("latitude")
            longitude = location_data.get("longitude")

            if latitude is None or longitude is None:
                self.logger.debug("Missing latitude or longitude in response")
                return None

            coords = (float(latitude), float(longitude))
            self.logger.debug(f"Parsed coordinates: {coords}")
            return coords

    def get_location_info(self) -> Optional[Dict[str, str]]:
        """
        Get detailed location information via IP geolocation.

        Returns:
            Dictionary containing location details or None if failed
        """
        self.logger.debug("Getting detailed location info")

        try:
            with timer(
                self.logger, f"detailed location request to {self.base_url}"
            ):
                response = requests.get(
                    self.base_url,
                    headers={"User-Agent": "weather-cli/1.0"},
                    timeout=10,
                )
                response.raise_for_status()

            location_data = response.json()

            # Check for error in response
            if location_data.get("error"):
                error_msg = location_data.get("reason", "Unknown error")
                self.logger.debug(f"API returned error: {error_msg}")
                return None

            # Extract useful location info
            info = {
                "city": location_data.get("city", "Unknown"),
                "region": location_data.get("region", "Unknown"),
                "country": location_data.get("country_name", "Unknown"),
                "country_code": location_data.get("country", "Unknown"),
                "timezone": location_data.get("timezone", "Unknown"),
            }

            self.logger.debug(f"Location info: {info}")
            return info

        except (requests.RequestException, ValueError, KeyError) as e:
            self.logger.debug(f"Failed to get location info: {e}")
            return None
