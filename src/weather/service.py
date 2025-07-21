"""Weather service for fetching weather data from API."""

from typing import Any, Dict, Optional

from weather.base_service import BaseAPIService
from weather.constants import OPENWEATHER_BASE_URL
from weather.types import Location
from weather.weather_art import WeatherArt


class WeatherService(BaseAPIService):
    """Service for fetching weather data from OpenWeatherMap API."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize weather service with API key."""
        super().__init__(OPENWEATHER_BASE_URL)
        self.api_key = api_key

    def get_weather(self, location: Location) -> Dict[str, Any]:
        """
        Get weather data for a location.

        Args:
            location: Location object with city or coordinates

        Returns:
            Dictionary containing weather data

        Raises:
            requests.RequestException: If API request fails
            ValueError: If API key is not provided
        """
        if not self.api_key:
            raise ValueError(
                "API key is required. Set OPENWEATHER_API_KEY environment "
                "variable."
            )

        if location.is_coordinates:
            lat, lon = location.coordinates
            params = {
                "lat": str(lat),
                "lon": str(lon),
                "appid": self.api_key,
                "units": "metric",
            }
        else:
            params = {
                "q": location.city_name,
                "appid": self.api_key,
                "units": "metric",
            }

        return self._make_request(params)

    def format_weather_output(self, weather_data: Dict[str, Any]) -> str:
        """
        Format weather data for display with ASCII art.

        Args:
            weather_data: Raw weather data from API

        Returns:
            Formatted weather string with ASCII art
        """
        city = weather_data["name"]
        country = weather_data["sys"]["country"]
        temp = weather_data["main"]["temp"]
        feels_like = weather_data["main"]["feels_like"]
        humidity = weather_data["main"]["humidity"]
        description = weather_data["weather"][0]["description"].title()
        weather_icon = weather_data["weather"][0]["icon"]

        weather_text = f"""Weather in {city}, {country}:
Temperature: {temp}°C (feels like {feels_like}°C)
Humidity: {humidity}%
Conditions: {description}"""

        return WeatherArt.format_weather_with_art(weather_icon, weather_text)
