# Weather CLI

A Python command-line weather application that fetches current weather data from OpenWeatherMap API.

Written as a vibe coding project with [Claude Code](https://claude.ai/code).

## Features

- 🌤️ Get weather for any city worldwide
- 📍 Enhanced 3-layer location detection (native GPS → IP geolocation → manual)
- 🛰️ Native system location support (macOS Core Location, Windows Location API, Linux GPSD)
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

## Enhanced Location Detection

The application features a sophisticated 3-layer location detection system for maximum accuracy and reliability:

### Location Resolution Priority
1. **Explicit city**: `--city "City Name"` (highest priority - always used when provided)
2. **Current location detection**: `--here` flag or automatic fallback
3. **Default city**: Configured in `config.yaml` (lowest priority)

### 3-Layer Location Detection System

When using `--here` or automatic location detection, the app tries these methods in order:

#### Layer 1: Native System Location (Most Accurate)
- **macOS**: Uses Core Location framework for GPS/WiFi positioning
  - Requires location permission: System Settings → Privacy & Security → Location Services
  - Enable location access for your terminal app (Terminal, iTerm2, etc.)
  - Provides sub-meter accuracy when GPS is available
- **Windows**: Uses Windows Location API via COM interface  
  - Requires Windows location services to be enabled
  - Uses GPS, WiFi, and cellular triangulation
- **Linux**: Uses GPSD daemon for GPS hardware
  - Requires GPSD service running and GPS hardware connected
  - Direct GPS satellite positioning

#### Layer 2: IP Geolocation (Reliable Fallback)
- Uses `ipapi.co` service for location based on IP address
- Works without any permissions or setup
- City-level accuracy (typically within 50-100km)
- Automatic fallback when native location fails or is unavailable

#### Layer 3: Configuration/Manual (Final Fallback)
- Uses default city from `config.yaml`
- Prompts for manual city input if no configuration

### Platform Dependencies

The application automatically installs platform-specific location libraries:
```toml
# Installed automatically based on your platform
pyobjc-framework-CoreLocation  # macOS only
pywin32                        # Windows only  
gpsd-py3                       # Linux only
```

### Location Permission Setup

**macOS Setup:**
1. Go to System Settings → Privacy & Security → Location Services
2. Ensure "Location Services" is enabled
3. Find your terminal app in the list (Terminal, iTerm2, etc.)
4. Enable location access for your terminal
5. Permission persists until manually revoked

**Windows Setup:**
1. Go to Settings → Privacy → Location
2. Ensure "Location service" is turned on
3. Allow apps to access location

**Linux Setup:**
1. Install and configure GPSD daemon: `sudo apt install gpsd gpsd-clients`
2. Connect GPS hardware (USB GPS receiver, etc.)
3. Start GPSD service: `sudo systemctl start gpsd`

## Usage

### Basic Usage

```bash
# Get weather for a specific city
poetry run weather --city "New York"

# Get weather for current location (uses 3-layer detection: GPS → IP → config)
poetry run weather --here

# Get weather automatically (uses current location if no default city configured)  
poetry run weather

# Debug mode shows which location method was used
poetry run weather --here --debug
```

**Example output:**
```
Weather in New York, US:                 │     \   |   /    
Temperature: 22.3°C (feels like 21.8°C)  │      .-.-.-.     
Humidity: 65%                            │   .- (  ☀️  ) -. 
Conditions: Clear Sky                    │      '-'-'-'     
                                         │     /   |   \    
```

**More examples:**
```
# Rainy weather
Weather in London, GB:                   │     \  |  /      
Temperature: 15.2°C (feels like 14.8°C)  │  .-.  ☀️  .-.    
Humidity: 78%                            │ (   ☁️☁️☁️   )   
Conditions: Light Rain                   │   '🌧️🌧️🌧️🌧️'  
                                         │    💧💧💧💧     

# Cloudy night
Weather in Tokyo, JP:                    │   *   🌙    *   
Temperature: 18.5°C (feels like 17.9°C)  │  .-.      .-.   
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

**Example debug output with location detection:**
```
2025-07-23 15:05:57,067Z DEBUG: weather.location - Attempting native system location...
2025-07-23 15:05:57,089Z INFO: weather.location - Using native location: (37.7749, -122.4194)
2025-07-23 15:05:57,089Z DEBUG: weather.cli - Starting weather lookup for coordinates: (37.7749, -122.4194)
2025-07-23 15:05:57,067Z DEBUG: weather.config - Completed configuration initialization in 0.001s
2025-07-23 15:05:57,395Z DEBUG: weather.service - Completed API request in 0.328s
2025-07-23 15:05:57,396Z DEBUG: weather.cli - Completed weather lookup in 0.330s
```

**Location fallback example:**
```
2025-07-23 15:05:57,067Z DEBUG: weather.location - Attempting native system location...
2025-07-23 15:05:57,089Z DEBUG: weather.location - CoreLocation framework not available
2025-07-23 15:05:57,089Z DEBUG: weather.location - Falling back to IP geolocation...
2025-07-23 15:05:57,234Z INFO: weather.location - Using IP geolocation: (37.7849, -122.4094)
```

## Command Line Options

```bash
poetry run weather --help
```

```
Options:
  --city TEXT  City name to get weather for (uses config default if not provided)
  --here       Use current location with 3-layer detection (GPS → IP → config)
  --debug      Enable debug mode with verbose logging and location method details
  --help       Show this message and exit
```

## Development

```bash
# Install dependencies
poetry install

# Setup configuration
cp config.example.yaml config.yaml
# Edit config.yaml and add your OpenWeather API key

# Run tests (100 tests total)
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
- **Enhanced Location Service** (`location.py`): 3-layer location detection (native GPS → IP → manual)
- **Configuration** (`config.py`): YAML config + environment variable management  
- **Service Layer** (`service.py`): OpenWeatherMap API integration
- **Weather Art** (`weather_art.py`): ASCII art representations with tab-based alignment
- **Error Handling** (`errors.py`): Centralized user-friendly error messages
- **Logging** (`logging_config.py`): Debug logging with UTC timestamps and timing

### Location Detection Flow
```
User runs --here
       ↓
1. Try Native GPS (Core Location/Windows API/GPSD)
       ↓ (if fails)
2. Try IP Geolocation (ipapi.co)
       ↓ (if fails)  
3. Use Config Default or Prompt for City
```

## Error Handling

The application provides user-friendly error messages for common issues:

- **Missing API key**: Clear instructions on how to configure
- **Invalid city**: "City not found" message
- **Network errors**: Connection failure details
- **API errors**: HTTP status code information

## License

This project is licensed under the MIT License.
