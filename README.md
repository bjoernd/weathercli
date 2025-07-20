# Weather CLI

A Python command-line weather application that fetches current weather data from OpenWeatherMap API with comprehensive debugging capabilities.

## Features

- 🌤️ Current weather information for any city

## Installation

```bash
poetry install
```

## Configuration

You need an OpenWeatherMap API key to use this application.

### Option 1: Environment Variable

```bash
export OPENWEATHER_API_KEY="your_api_key_here"
```

### Option 2: Configuration File

1. Copy the example configuration:
   ```bash
   cp config.example.yaml config.yaml
   ```

2. Edit `config.yaml` and add your API key and optional default city:
   ```yaml
   api:
     openweather:
       key: "your_api_key_here"

   defaults:
     city: "London"  # Optional: default city when --city not specified
   ```

**Get your free API key**: [OpenWeatherMap API](https://openweathermap.org/api)

## Usage

### Basic Usage

```bash
# Get weather for a specific city
poetry run weather --city "New York"

# Get weather for default city (configured in config.yaml)
poetry run weather
```

**Example output:**
```
Weather in New York, US:
Temperature: 22.3°C (feels like 21.8°C)
Humidity: 65%
Conditions: Clear Sky
```

### Debug Mode

Enable comprehensive logging and timing information:

```bash
poetry run weather --city "London" --debug
```

**Debug features:**
- 📊 Detailed timing for all operations
- 🕐 UTC timestamps on all log entries
- 📝 Logs written to both console and `weather_debug.log`
- 🔍 API request/response details
- ⚡ Performance bottleneck identification

**Example debug output:**
```
2025-07-20 15:05:57,067Z DEBUG: weather.cli - Starting weather lookup for city: London
2025-07-20 15:05:57,067Z DEBUG: weather.config - Completed configuration initialization in 0.001s
2025-07-20 15:05:57,395Z DEBUG: weather.service - Completed API request in 0.328s
2025-07-20 15:05:57,396Z DEBUG: weather.cli - Completed weather lookup for city: London in 0.330s
```

## Command Line Options

```bash
poetry run weather --help
```

```
Options:
  --city TEXT  City name to get weather for (uses config default if not provided)
  --debug      Enable debug mode with verbose logging
  --help       Show this message and exit
```

## Development

```bash
# Install dependencies
poetry install

# Setup configuration
cp config.example.yaml config.yaml
# Edit config.yaml and add your OpenWeather API key

# Run tests (52 tests total)
poetry run pytest                        # All tests
poetry run pytest tests/test_cli.py      # CLI tests only
poetry run pytest tests/test_service.py  # Service tests only
poetry run pytest -v                     # Verbose output

# Code formatting and linting
poetry run black .                       # Format code
poetry run isort .                       # Sort imports
poetry run flake8                        # Lint code
poetry run mypy src/                     # Type checking

# All linting in one command
poetry run black . && poetry run isort . && poetry run flake8 && poetry run mypy src/
```

## Architecture

- **CLI Layer** (`cli.py`): Click-based command-line interface
- **Configuration** (`config.py`): YAML config + environment variable management
- **Service Layer** (`service.py`): OpenWeatherMap API integration
- **Logging** (`logging_config.py`): Debug logging with UTC timestamps and timing

## Error Handling

The application provides user-friendly error messages for common issues:

- **Missing API key**: Clear instructions on how to configure
- **Invalid city**: "City not found" message
- **Network errors**: Connection failure details
- **API errors**: HTTP status code information

## License

This project is licensed under the MIT License.
