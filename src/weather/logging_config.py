"""Logging configuration for the weather application."""

import logging
import sys
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Generator, Optional


class UTCFormatter(logging.Formatter):
    """Custom formatter that uses UTC timestamps."""

    def formatTime(self, record, datefmt=None):
        """Override formatTime to use UTC."""
        if datefmt:
            return datetime.utcfromtimestamp(record.created).strftime(datefmt)
        else:
            return (
                datetime.utcfromtimestamp(record.created).strftime(
                    "%Y-%m-%d %H:%M:%S,%f"
                )[:-3]
                + "Z"
            )


def setup_logging(
    debug: bool = False, log_file: Optional[Path] = None
) -> None:
    """
    Set up logging configuration for the application.

    Args:
        debug: Enable debug mode with verbose logging
        log_file: Optional log file path. Defaults to weather_debug.log
                 in current directory when debug is True
    """
    if not debug:
        # Disable all logging in normal mode
        logging.disable(logging.CRITICAL)
        return

    # Enable logging and set debug level
    logging.disable(logging.NOTSET)

    if log_file is None:
        log_file = Path.cwd() / "weather_debug.log"

    # Create formatters with UTC timestamps
    file_formatter = UTCFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_formatter = UTCFormatter(
        "%(asctime)s DEBUG: %(name)s - %(message)s"
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # File handler for debug logs
    file_handler = logging.FileHandler(log_file, mode="a")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # Console handler for debug output
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # Log startup message
    logger = logging.getLogger(__name__)
    logger.debug(f"Debug logging enabled. Log file: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


@contextmanager
def timer(
    logger: logging.Logger, operation: str
) -> Generator[None, None, None]:
    """
    Context manager to time operations and log the duration.

    Args:
        logger: Logger instance to use for timing logs
        operation: Description of the operation being timed

    Yields:
        None
    """
    start_time = time.perf_counter()
    logger.debug(f"Starting {operation}")
    try:
        yield
    finally:
        end_time = time.perf_counter()
        duration = end_time - start_time
        logger.debug(f"Completed {operation} in {duration:.3f}s")


def log_timing(
    logger: logging.Logger, operation: str, duration: float
) -> None:
    """
    Log timing information for an operation.

    Args:
        logger: Logger instance to use
        operation: Description of the operation
        duration: Duration in seconds
    """
    logger.debug(f"{operation} took {duration:.3f}s")
