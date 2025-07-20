"""Command line interface for the weather application."""

import click
import requests

from weather.config import Config
from weather.errors import ErrorHandler
from weather.location_resolver import LocationResolver
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
    setup_logging(debug=debug)
    logger = get_logger(__name__)
    location = None

    try:
        with timer(logger, "configuration initialization"):
            config = Config()

        with timer(logger, "location resolution"):
            resolver = LocationResolver(config)
            location = resolver.resolve_location(here, city)

        if not location:
            ErrorHandler.handle_location_resolution_failure()

        api_key = config.get_api_key("openweather")
        if not api_key:
            ErrorHandler.handle_missing_api_key()

        assert location is not None
        with timer(logger, f"weather lookup for {location.description}"):
            weather_service = WeatherService(api_key)
            weather_data = weather_service.get_weather(location)
            formatted_output = weather_service.format_weather_output(
                weather_data
            )
            click.echo(formatted_output)

    except requests.RequestException as e:
        if location:
            ErrorHandler.handle_weather_api_error(e, location)
        else:
            ErrorHandler.handle_location_service_error(e)
    except ValueError as e:
        click.echo(f"Error: {e}")
        raise click.Abort()
    except Exception as e:
        ErrorHandler.handle_unexpected_error(e)


if __name__ == "__main__":
    main()
