"""Error handling utilities for the weather application."""

import click
import requests

from weather.types import Location


class ErrorHandler:
    """Centralized error handling and user messaging."""

    @staticmethod
    def handle_missing_api_key() -> None:
        """Handle missing API key error."""
        click.echo("Error: OpenWeather API key not found.")
        click.echo("Please set it in one of these ways:")
        click.echo(
            "1. Environment variable: export OPENWEATHER_API_KEY=your_key"
        )
        click.echo("2. Config file (config.yaml):")
        click.echo("   api:")
        click.echo("     openweather:")
        click.echo("       key: your_api_key_here")
        click.echo("")
        click.echo(
            "Get your free API key from: https://openweathermap.org/api"
        )
        raise click.Abort()

    @staticmethod
    def handle_location_resolution_failure() -> None:
        """Handle failure to resolve location."""
        click.echo("Error: Could not determine location.")
        click.echo("Either:")
        click.echo("1. Use --city 'City Name' to specify a city")
        click.echo("2. Configure a default city in config.yaml:")
        click.echo("   defaults:")
        click.echo("     city: 'Your City'")
        raise click.Abort()

    @staticmethod
    def handle_location_service_error(error: Exception) -> None:
        """Handle location service errors."""
        click.echo(f"Error: Failed to get current location - {error}.")
        click.echo("Try specifying a city with --city instead.")
        raise click.Abort()

    @staticmethod
    def handle_weather_api_error(
        error: requests.RequestException, location: Location
    ) -> None:
        """Handle weather API errors."""
        if hasattr(error, "response") and error.response is not None:
            status_code = error.response.status_code
            if status_code == 404:
                if location.is_coordinates:
                    lat, lon = location.coordinates
                    click.echo(
                        f"Error: No weather data found for coordinates "
                        f"{lat:.2f}, {lon:.2f}."
                    )
                else:
                    click.echo(
                        f"Error: City '{location.city_name}' not found."
                    )
            elif status_code == 401:
                click.echo("Error: Invalid API key.")
            else:
                click.echo(
                    f"Error: API request failed with status {status_code}"
                )
        else:
            if location.is_coordinates:
                lat, lon = location.coordinates
                click.echo(
                    f"Error: Network request failed for coordinates "
                    f"{lat:.2f}, {lon:.2f} - {error}"
                )
            else:
                click.echo(
                    f"Error: Network request failed for {location.city_name} "
                    f"- {error}"
                )
        raise click.Abort()

    @staticmethod
    def handle_unexpected_error(error: Exception) -> None:
        """Handle unexpected errors."""
        click.echo(f"Unexpected error: {error}")
        raise click.Abort()
