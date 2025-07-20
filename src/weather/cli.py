"""Command line interface for the weather application."""

import click
import requests

from weather.config import Config
from weather.service import WeatherService


@click.command()
@click.option("--city", required=True, help="City name to get weather for")
def main(city: str) -> None:
    """Get weather information for a city."""
    config = Config()
    api_key = config.get_api_key("openweather")

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

    try:
        weather_data = weather_service.get_weather(city)
        formatted_output = weather_service.format_weather_output(weather_data)
        click.echo(formatted_output)
    except requests.RequestException as e:
        if hasattr(e, "response") and e.response is not None:
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
        click.echo(f"Error: {e}")
        raise click.Abort()
    except Exception as e:
        click.echo(f"Unexpected error: {e}")
        raise click.Abort()


if __name__ == "__main__":
    main()
