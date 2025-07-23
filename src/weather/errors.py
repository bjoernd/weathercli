"""Error handling utilities for the weather application."""

import click
import requests

from weather.types import Location


class ErrorHandler:
    """Centralized error handling and user messaging."""

    @staticmethod
    def handle_missing_api_key() -> None:
        """Handle missing API key error."""
        message = """Error: OpenWeather API key not found.
Please set it in one of these ways:
1. Environment variable: export OPENWEATHER_API_KEY=your_key
2. Config file (config.yaml):
   api:
     openweather:
       key: your_api_key_here

Get your free API key from: https://openweathermap.org/api"""
        click.echo(message)
        raise click.Abort()

    @staticmethod
    def handle_location_resolution_failure() -> None:
        """Handle failure to resolve location."""
        message = """Error: Could not determine location.
Either:
1. Use --city 'City Name' to specify a city
2. Configure a default city in config.yaml:
   defaults:
     city: 'Your City'"""
        click.echo(message)
        raise click.Abort()

    @staticmethod
    def handle_location_service_error(error: Exception) -> None:
        """Handle location service errors."""
        message = f"Error: Failed to get current location - {error}.\nTry specifying a city with --city instead."
        click.echo(message)
        raise click.Abort()

    @staticmethod
    def handle_weather_api_error(
        error: requests.RequestException, location: Location
    ) -> None:
        """Handle weather API errors."""
        if hasattr(error, "response") and error.response is not None:
            message = ErrorHandler._format_http_error(error.response.status_code, location)
        else:
            message = ErrorHandler._format_network_error(error, location)
        
        click.echo(message)
        raise click.Abort()
    
    @staticmethod
    def _format_http_error(status_code: int, location: Location) -> str:
        """Format HTTP error messages based on status code."""
        if status_code == 404:
            if location.is_coordinates:
                lat, lon = location.coordinates
                return f"Error: No weather data found for coordinates {lat:.2f}, {lon:.2f}."
            else:
                return f"Error: City '{location.city_name}' not found."
        elif status_code == 401:
            return "Error: Invalid API key."
        else:
            return f"Error: API request failed with status {status_code}"
    
    @staticmethod
    def _format_network_error(error: Exception, location: Location) -> str:
        """Format network error messages."""
        if location.is_coordinates:
            lat, lon = location.coordinates
            return f"Error: Network request failed for coordinates {lat:.2f}, {lon:.2f} - {error}"
        else:
            return f"Error: Network request failed for {location.city_name} - {error}"
    

    @staticmethod
    def handle_unexpected_error(error: Exception) -> None:
        """Handle unexpected errors."""
        click.echo(f"Unexpected error: {error}")
        raise click.Abort()
