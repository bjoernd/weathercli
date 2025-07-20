"""Weather service for fetching weather data from API."""

from typing import Any, Dict, Optional

import requests


class WeatherService:
    """Service for fetching weather data from OpenWeatherMap API."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize weather service with API key."""
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, city: str) -> Dict[str, Any]:
        """
        Get weather data for a city.

        Args:
            city: Name of the city

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

        params = {"q": city, "appid": self.api_key, "units": "metric"}

        response = requests.get(self.base_url, params=params)
        response.raise_for_status()

        return response.json()

    def format_weather_output(self, weather_data: Dict[str, Any]) -> str:
        """
        Format weather data for display.

        Args:
            weather_data: Raw weather data from API

        Returns:
            Formatted weather string
        """
        city = weather_data["name"]
        country = weather_data["sys"]["country"]
        temp = weather_data["main"]["temp"]
        feels_like = weather_data["main"]["feels_like"]
        humidity = weather_data["main"]["humidity"]
        description = weather_data["weather"][0]["description"].title()

        return f"""Weather in {city}, {country}:
Temperature: {temp}°C (feels like {feels_like}°C)
Humidity: {humidity}%
Conditions: {description}"""
