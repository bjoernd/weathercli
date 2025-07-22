# Weather CLI

A Python command-line weather application that fetches current weather data from OpenWeatherMap API.

Written as a vibe coding project with [Claude Code](https://claude.ai/code).

## Features

- 🌤️ Get weather for any city worldwide
- 📍 Automatic current location detection  
- ⚙️ Simple configuration setup
- 🏠 Set a default city for quick access
- 🔍 Debug mode for troubleshooting

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

## How Location Detection Works

The application determines your location in this priority order:

1. **Explicit city**: `--city "City Name"` (highest priority)
2. **Current location**: `--here` or automatic detection
3. **Default city**: Configured in `config.yaml` (lowest priority)

When you run `poetry run weather` without any options:
- If a default city is configured, it uses that
- If no default city is configured, it automatically detects your current location using IP geolocation

## Usage

### Basic Usage

```bash
# Get weather for a specific city
poetry run weather --city "New York"

# Get weather for current location (using IP geolocation)
poetry run weather --here

# Get weather automatically (uses current location if no default city configured)
poetry run weather
```

**Example output:**
```
Weather in New York, US:                │     \   |   /    
Temperature: 22.3°C (feels like 21.8°C) │      .-.-.-.     
Humidity: 65%                            │   .- (  ☀️  ) -. 
Conditions: Clear Sky                    │      '-'-'-'     
                                         │     /   |   \    
```

**More examples:**
```
# Rainy weather
Weather in London, GB:                  │     \  |  /      
Temperature: 15.2°C (feels like 14.8°C) │  .-.  ☀️  .-.    
Humidity: 78%                            │ (   ☁️☁️☁️   )   
Conditions: Light Rain                   │   '🌧️🌧️🌧️🌧️'  
                                         │    💧💧💧💧     

# Cloudy night
Weather in Tokyo, JP:                   │   *   🌙    *   
Temperature: 18.5°C (feels like 17.9°C) │  .-.      .-.   
Humidity: 72%                            │ (   ☁️☁️☁️   )  
Conditions: Few Clouds                   │  '-'     '-'    
                                         │    *        *   
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
  --here       Use current location based on IP geolocation
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

# Run tests (96 tests total)
poetry run pytest                        # All tests
poetry run pytest tests/test_cli.py      # CLI tests only
poetry run pytest tests/test_service.py  # Service tests only
poetry run pytest tests/test_weather_art.py  # Weather art tests only
poetry run pytest -v                     # Verbose output

# Code formatting and linting
poetry run black .                       # Format code
poetry run isort .                       # Sort imports
poetry run flake8                        # Lint code
poetry run mypy src/                     # Type checking

# All linting in one command
poetry run black . && poetry run isort . && poetry run flake8 && poetry run mypy src/
```

## Visual Weather Patterns

The application displays ASCII art representations for all weather conditions:

- ☀️ **Clear skies** - Sun with rays (day) or moon with stars (night)
- ☁️ **Cloudy conditions** - Various cloud formations from few to overcast
- 🌧️ **Rain** - Clouds with raindrops, from light drizzle to heavy rain
- ❄️ **Snow** - Clouds with snowflakes
- ⛈️ **Thunderstorms** - Dark clouds with lightning and rain
- 🌫️ **Mist/Fog** - Atmospheric patterns for low visibility

## Architecture

- **CLI Layer** (`cli.py`): Click-based command-line interface
- **Location Resolution** (`location_resolver.py`): Smart location detection with fallback priority
- **Configuration** (`config.py`): YAML config + environment variable management  
- **Service Layer** (`service.py`): OpenWeatherMap API integration
- **Weather Art** (`weather_art.py`): ASCII art representations with tab-based alignment
- **Error Handling** (`errors.py`): Centralized user-friendly error messages
- **Logging** (`logging_config.py`): Debug logging with UTC timestamps and timing

## Error Handling

The application provides user-friendly error messages for common issues:

- **Missing API key**: Clear instructions on how to configure
- **Invalid city**: "City not found" message
- **Network errors**: Connection failure details
- **API errors**: HTTP status code information

## License

This project is licensed under the MIT License.
