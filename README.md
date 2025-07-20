# Weather

A Python weather application.

## Installation

```bash
poetry install
```

## Usage

```bash
poetry run weather --city "New York"
```

## Development

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Format code
poetry run black .
poetry run isort .

# Lint
poetry run flake8

# Type checking
poetry run mypy src/
```