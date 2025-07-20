"""Location resolution service for the weather application."""

from typing import Optional

import requests

from weather.config import Config
from weather.location import LocationService
from weather.types import Location


class LocationResolver:
    """Resolves location based on various inputs and fallbacks."""

    def __init__(self, config: Config):
        """Initialize resolver with config."""
        self.config = config
        self.location_service = LocationService()

    def resolve_location(
        self, here: bool, city: Optional[str]
    ) -> Optional[Location]:
        """
        Resolve location with priority: here flag > city arg > default > auto.

        Args:
            here: Use current location flag
            city: Explicit city name

        Returns:
            Location object or None if resolution fails
        """
        if here:
            return self._get_current_location()

        if city:
            return Location.from_city(city)

        default_city = self.config.get_default_city()
        if default_city:
            return Location.from_city(default_city)

        return self._get_current_location()

    def _get_current_location(self) -> Optional[Location]:
        """Get current location via IP geolocation."""
        try:
            coords = self.location_service.get_current_location()
            if coords:
                lat, lon = coords
                return Location.from_coordinates(lat, lon)
        except (requests.RequestException, ValueError):
            pass
        return None
