"""Weather service for fetching weather data from API."""

from typing import Any, Dict, Optional, Tuple, Union

import requests

from weather.logging_config import get_logger, timer


class WeatherService:
    """Service for fetching weather data from OpenWeatherMap API."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize weather service with API key."""
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.logger = get_logger(__name__)
        self.logger.debug("WeatherService initialized with API key")
        self.logger.debug(f"Base URL: {self.base_url}")

    def get_weather(
        self, location: Union[str, Tuple[float, float]]
    ) -> Dict[str, Any]:
        """
        Get weather data for a city or coordinates.

        Args:
            location: City name or tuple of (latitude, longitude)

        Returns:
            Dictionary containing weather data

        Raises:
            requests.RequestException: If API request fails
            ValueError: If API key is not provided
        """
        if isinstance(location, tuple):
            lat, lon = location
            self.logger.debug(f"Getting weather for coordinates: {lat}, {lon}")
        else:
            self.logger.debug(f"Getting weather for city: {location}")

        if not self.api_key:
            self.logger.debug("API key validation failed")
            raise ValueError(
                "API key is required. Set OPENWEATHER_API_KEY environment "
                "variable."
            )

        # Build parameters based on location type
        if isinstance(location, tuple):
            lat, lon = location
            params = {
                "lat": str(lat),
                "lon": str(lon),
                "appid": self.api_key,
                "units": "metric",
            }
        else:
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric",
            }

        self.logger.debug(f"Request parameters: {params}")

        with timer(self.logger, f"API request to {self.base_url}"):
            self.logger.debug(f"Making API request to: {self.base_url}")
            response = requests.get(self.base_url, params=params)
            self.logger.debug(f"API response status: {response.status_code}")

            response.raise_for_status()

        with timer(self.logger, "JSON response parsing"):
            weather_data = response.json()
            keys = list(weather_data.keys())
            self.logger.debug(f"Weather data keys: {keys}")

        return weather_data

    def format_weather_output(self, weather_data: Dict[str, Any]) -> str:
        """
        Format weather data for display.

        Args:
            weather_data: Raw weather data from API

        Returns:
            Formatted weather string
        """
        with timer(self.logger, "weather data formatting"):
            self.logger.debug("Formatting weather data for output")

            city = weather_data["name"]
            country = weather_data["sys"]["country"]
            temp = weather_data["main"]["temp"]
            feels_like = weather_data["main"]["feels_like"]
            humidity = weather_data["main"]["humidity"]
            description = weather_data["weather"][0]["description"].title()

            self.logger.debug(f"Formatted data - City: {city}, Temp: {temp}°C")

            return f"""Weather in {city}, {country}:
Temperature: {temp}°C (feels like {feels_like}°C)
Humidity: {humidity}%
Conditions: {description}"""
