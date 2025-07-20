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
poetry run pytest

# Code formatting and linting
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
- `src/weather/__init__.py` - Package initialization
- `src/weather/cli.py` - Command line interface entry point
- `tests/` - Test files
- `pyproject.toml` - Poetry configuration and dependencies

## Architecture Notes

- Uses Poetry for dependency management and packaging
- CLI built with Click framework
- Package follows src-layout structure
- Python 3.10+ required
- Entry point configured as `weather` command

## Error Handling Guidelines

- Exit with an error whenever a command line invocation fails with a missing tool or program. Ask the user how to proceed.

## Development Best Practices

- Linting: after every code change, run a linter.
- Testing: after every code change, run poetry testing and fix all failures.