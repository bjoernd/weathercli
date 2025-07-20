"""Command line interface for the weather application."""

import click
import requests

from weather.config import Config
from weather.logging_config import get_logger, setup_logging, timer
from weather.service import WeatherService


@click.command()
@click.option("--city", required=True, help="City name to get weather for")
@click.option(
    "--debug", is_flag=True, help="Enable debug mode with verbose logging"
)
def main(city: str, debug: bool) -> None:
    """Get weather information for a city."""
    # Setup logging based on debug flag
    setup_logging(debug=debug)
    logger = get_logger(__name__)

    with timer(logger, f"weather lookup for city: {city}"):
        logger.debug(f"Starting weather lookup for city: {city}")
        logger.debug(f"Debug mode: {debug}")

        with timer(logger, "configuration initialization"):
            config = Config()
            api_key = config.get_api_key("openweather")

        logger.debug(f"API key configured: {'Yes' if api_key else 'No'}")

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
                logger.debug(f"Fetching weather data for: {city}")
                weather_data = weather_service.get_weather(city)
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
                    click.echo(f"Error: City '{city}' not found.")
                elif e.response.status_code == 401:
                    click.echo("Error: Invalid API key.")
                else:
                    click.echo(
                        f"Error: API request failed with status "
                        f"{e.response.status_code}"
                    )
            else:
                click.echo(f"Error: Network request failed - {e}")
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
