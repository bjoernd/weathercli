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
   ```

3. **Setup**: Copy `config.example.yaml` to `config.yaml` and add your API key
4. **Security**: `config.yaml` is git-ignored and never tracked

## Development Commands

```bash
# Install dependencies
poetry install

# Setup configuration
cp config.example.yaml config.yaml
# Edit config.yaml and add your OpenWeather API key

# Run the CLI application
poetry run weather --city "New York"

# Run tests
poetry run pytest                        # Run all tests (52 total)
poetry run pytest tests/test_config.py   # Run single test file
poetry run pytest tests/test_cli.py -v   # Run CLI tests with verbose output
poetry run pytest tests/test_service.py  # Run WeatherService tests

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
- `tests/` - Comprehensive test suite (52 tests total)
  - `test_cli.py` - CLI functionality and error handling tests
  - `test_config.py` - Configuration system tests
  - `test_service.py` - WeatherService API integration tests
- `config.example.yaml` - Template configuration file
- `pyproject.toml` - Poetry configuration and dependencies

## Architecture Notes

- Uses Poetry for dependency management and packaging
- CLI built with Click framework for command-line interface
- Package follows src-layout structure
- Python 3.10+ required
- Entry point configured as `weather` command
- Configuration system: Environment variables override YAML config
- Error handling: Comprehensive HTTP error codes and user-friendly messages
- Weather data fetched from OpenWeatherMap API in metric units
- Test coverage: All components have comprehensive unit tests with mocking
- Three-layer architecture: CLI → Config/Service → External API

## Error Handling Guidelines

- Exit with an error whenever a command line invocation fails with a missing tool or program. Ask the user how to proceed.

## Development Best Practices

- Linting: after every code change, run `poetry run black . && poetry run isort . && poetry run flake8 && poetry run mypy src/` and fix all reported issues
- Testing: after every code change, run `poetry run pytest` and fix all failures

## Code Style Guidelines

- When generating code, make sure that no line ever gets longer than 79 characters.
