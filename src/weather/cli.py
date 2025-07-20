"""Command line interface for the weather application."""

from typing import Tuple, Union

import click
import requests

from weather.config import Config
from weather.location import LocationService
from weather.logging_config import get_logger, setup_logging, timer
from weather.service import WeatherService


@click.command()
@click.option(
    "--city",
    help="City name to get weather for (uses config default if not provided)",
)
@click.option(
    "--here",
    is_flag=True,
    help="Use current location based on IP geolocation",
)
@click.option(
    "--debug", is_flag=True, help="Enable debug mode with verbose logging"
)
def main(city: str | None, here: bool, debug: bool) -> None:
    """Get weather information for a city or current location."""
    # Setup logging based on debug flag
    setup_logging(debug=debug)
    logger = get_logger(__name__)

    logger.debug(f"Debug mode: {debug}")

    with timer(logger, "configuration initialization"):
        config = Config()
        api_key = config.get_api_key("openweather")

    logger.debug(f"API key configured: {'Yes' if api_key else 'No'}")

    # Determine location: priority is --here, then --city, then
    # default
    location: Union[str, Tuple[float, float], None] = None
    location_description = ""

    if here:
        logger.debug("Getting current location via IP geolocation")
        try:
            with timer(logger, "IP geolocation lookup"):
                location_service = LocationService()
                coords = location_service.get_current_location()
                if coords:
                    location = coords
                    lat, lon = coords
                    location_description = f"coordinates {lat:.2f}, {lon:.2f}"
                    logger.debug(
                        f"Using current location: {location_description}"
                    )
                else:
                    click.echo(
                        "Error: Could not determine current location. "
                        "Try specifying a city with --city instead."
                    )
                    raise click.Abort()
        except (requests.RequestException, ValueError) as e:
            logger.debug(f"Location service error: {e}")
            click.echo(
                f"Error: Failed to get current location - {e}. "
                "Try specifying a city with --city instead."
            )
            raise click.Abort()
    elif city:
        logger.debug(f"Using city from command line: {city}")
        location = city
        location_description = f"city {city}"
    else:
        # Handle default city if neither --here nor --city provided
        logger.debug("No location options provided, checking for default city")
        city = config.get_default_city()
        if city:
            logger.debug(f"Using default city from config: {city}")
            location = city
            location_description = f"default city {city}"
        else:
            # No default city configured, automatically use current location
            logger.debug("No default city configured, using current location")
            try:
                with timer(logger, "IP geolocation lookup"):
                    location_service = LocationService()
                    coords = location_service.get_current_location()
                    if coords:
                        location = coords
                        lat, lon = coords
                        location_description = (
                            f"coordinates {lat:.2f}, {lon:.2f}"
                        )
                        logger.debug(
                            f"Using current location: {location_description}"
                        )
                    else:
                        click.echo(
                            "Error: Could not determine current location."
                        )
                        click.echo("Either:")
                        click.echo(
                            "1. Use --city 'City Name' to specify a city"
                        )
                        click.echo(
                            "2. Configure a default city in config.yaml:"
                        )
                        click.echo("   defaults:")
                        click.echo("     city: 'Your City'")
                        raise click.Abort()
            except (requests.RequestException, ValueError) as e:
                logger.debug(f"Location service error: {e}")
                click.echo(f"Error: Failed to get current location - {e}.")
                click.echo("Either:")
                click.echo("1. Use --city 'City Name' to specify a city")
                click.echo("2. Configure a default city in config.yaml:")
                click.echo("   defaults:")
                click.echo("     city: 'Your City'")
                raise click.Abort()

    with timer(logger, f"weather lookup for {location_description}"):
        logger.debug(f"Starting weather lookup for {location_description}")

        if not api_key:
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

        weather_service = WeatherService(api_key)
        logger.debug("WeatherService initialized")

        try:
            with timer(logger, "weather data fetch and format"):
                logger.debug(
                    f"Fetching weather data for: {location_description}"
                )
                assert (
                    location is not None
                )  # Should be guaranteed by logic above
                weather_data = weather_service.get_weather(location)
                logger.debug("Weather data retrieved successfully")

                formatted_output = weather_service.format_weather_output(
                    weather_data
                )
                logger.debug("Weather data formatted for output")
            click.echo(formatted_output)
        except requests.RequestException as e:
            logger.debug(f"RequestException occurred: {e}")
            if hasattr(e, "response") and e.response is not None:
                logger.debug(f"Response status code: {e.response.status_code}")
                if e.response.status_code == 404:
                    if isinstance(location, tuple):
                        lat, lon = location
                        click.echo(
                            f"Error: No weather data found for coordinates "
                            f"{lat:.2f}, {lon:.2f}."
                        )
                    else:
                        click.echo(f"Error: City '{location}' not found.")
                elif e.response.status_code == 401:
                    click.echo("Error: Invalid API key.")
                else:
                    click.echo(
                        f"Error: API request failed with status "
                        f"{e.response.status_code}"
                    )
            else:
                if isinstance(location, tuple):
                    lat, lon = location
                    click.echo(
                        f"Error: Network request failed for coordinates "
                        f"{lat:.2f}, {lon:.2f} - {e}"
                    )
                else:
                    click.echo(
                        f"Error: Network request failed for {location} - {e}"
                    )
            raise click.Abort()
        except ValueError as e:
            logger.debug(f"ValueError occurred: {e}")
            click.echo(f"Error: {e}")
            raise click.Abort()
        except Exception as e:
            logger.debug(f"Unexpected exception occurred: {e}")
            click.echo(f"Unexpected error: {e}")
            raise click.Abort()


if __name__ == "__main__":
    main()
