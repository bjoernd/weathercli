# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python weather application built with Poetry for dependency management. The application provides a CLI interface for getting weather information.

## Configuration

The application uses a YAML-based configuration system:

1. **Environment variables** (checked first):
   - `OPENWEATHER_API_KEY`: OpenWeather API key

2. **Config file** (`config.yaml` in project root):
   ```yaml
   api:
     openweather:
       key: "your_api_key_here"
   defaults:
     city: "London"  # Optional default city
   ```

3. **Setup**: Copy `config.example.yaml` to `config.yaml` and add your API key
4. **Security**: `config.yaml` is git-ignored and never tracked

## Location Services

The application features an enhanced 3-layer location detection system:

### 1. Native System Location (Layer 1 - Most Accurate)
- **macOS**: Uses Core Location framework for GPS/WiFi positioning
  - Requires location permissions: System Settings → Privacy & Security → Location Services
  - Enable location access for your terminal application (Terminal, iTerm2, etc.)
  - May show permission dialog on first use
- **Windows**: Uses Windows Location API via COM interface
  - Requires location services enabled in Windows settings
- **Linux**: Uses GPSD daemon for GPS hardware
  - Requires GPSD service running and GPS hardware

### 2. IP Geolocation (Layer 2 - Fallback)
- Uses `ipapi.co` service for approximate location based on IP address
- Works without permissions but less accurate
- Automatic fallback when native location fails

### 3. Manual/Configuration (Layer 3 - Final Fallback)
- Uses default city from configuration
- Accepts manual city input via `--city` argument

### Platform-Specific Dependencies
The application automatically installs platform-specific dependencies:
- `pyobjc-framework-CoreLocation` (macOS only)
- `pywin32` (Windows only)
- `gpsd-py3` (Linux only)

### Location Usage
```bash
poetry run weather --here              # Uses 3-layer location detection
poetry run weather --here --debug      # Shows which location method is used
poetry run weather --city "London"     # Manual city override
```

## Development Commands

```bash
# Install dependencies
poetry install

# Setup configuration
cp config.example.yaml config.yaml
# Edit config.yaml and add your OpenWeather API key

# Run the CLI application
poetry run weather --city "New York"
poetry run weather --here              # Use current location
poetry run weather --debug            # Enable debug logging

# Run tests
poetry run pytest                        # Run all tests (100 total)
poetry run pytest tests/test_config.py   # Run single test file
poetry run pytest tests/test_cli.py -v   # Run CLI tests with verbose output
poetry run pytest tests/test_service.py  # Run WeatherService tests
poetry run pytest tests/test_location.py # Run LocationService tests
poetry run pytest tests/test_weather_art.py # Run WeatherArt tests

# Code formatting and linting (run after every code change)
poetry run black .
poetry run isort .
poetry run flake8
poetry run mypy src/

# Install new dependencies
poetry add <package>              # Runtime dependency
poetry add --group dev <package>  # Development dependency
```

## Project Structure

- `src/weather/` - Main package source code
- `src/weather/cli.py` - Command line interface entry point with Click commands
- `src/weather/config.py` - Configuration management (YAML + env vars)  
- `src/weather/service.py` - WeatherService for OpenWeatherMap API integration
- `src/weather/location.py` - Enhanced LocationService with native GPS and IP geolocation fallback
- `src/weather/location_resolver.py` - Location resolution with fallback priority
- `src/weather/base_service.py` - Shared API service base class with timing
- `src/weather/weather_art.py` - ASCII art representations for weather conditions
- `src/weather/types.py` - Location dataclass and common types
- `src/weather/errors.py` - Centralized error handling with user-friendly messages
- `src/weather/constants.py` - Configuration constants and API endpoints
- `src/weather/logging_config.py` - Centralized logging with UTC timestamps and timing
- `tests/` - Comprehensive test suite (100 tests total)
  - `test_cli.py` - CLI functionality and error handling tests (27 tests)
  - `test_config.py` - Configuration system tests (19 tests)
  - `test_service.py` - WeatherService API integration tests (24 tests)
  - `test_location.py` - Enhanced LocationService tests including native GPS (17 tests)
  - `test_weather_art.py` - WeatherArt ASCII art tests (13 tests)
- `config.example.yaml` - Template configuration file
- `pyproject.toml` - Poetry configuration and dependencies

## Architecture Notes

- Uses Poetry for dependency management and packaging
- CLI built with Click framework for command-line interface
- Package follows src-layout structure with separation of concerns
- Python 3.10+ required
- Entry point configured as `weather` command
- Configuration system: Environment variables override YAML config with dot notation support
- Error handling: Comprehensive HTTP error codes and user-friendly messages via ErrorHandler class
- Weather data fetched from OpenWeatherMap API in metric units
- Test coverage: All components have comprehensive unit tests with extensive mocking
- Five-layer architecture: CLI → LocationResolver → Config/Service/Location → BaseAPIService → External APIs
- Location resolution priority: `--here` flag → `--city` argument → default city → automatic current location
- Debug mode provides comprehensive logging with file output and performance timing
- Enhanced location detection with 3-layer fallback system:
  1. Native system location (GPS/WiFi positioning via Core Location on macOS, Windows Location API, Linux GPSD)
  2. IP-based geolocation via ipapi.co for automatic location detection
  3. Configuration defaults and manual city input
- Shared BaseAPIService class provides common HTTP request handling with timing and error handling
- Location abstraction supports both city names and coordinate-based lookups
- Strong typing throughout with dataclasses and type hints
- Display format: Weather data is displayed on the left side with a vertical line separator (│) and ASCII art aligned to the right for clear visual separation and consistent alignment in monospaced terminals

## Error Handling Guidelines

- Exit with an error whenever a command line invocation fails with a missing tool or program. Ask the user how to proceed.

## Development Best Practices

- Linting: after every code change, run `poetry run black . && poetry run isort . && poetry run flake8 && poetry run mypy src/` and fix all reported issues
- Testing: after every code change, run `poetry run pytest` and fix all failures

## Code Style Guidelines

- When generating code, make sure that no line ever gets longer than 79 characters.
