"""Base service class for API interactions."""

from typing import Any, Dict, Optional

import requests

from weather.constants import API_TIMEOUT
from weather.logging_config import get_logger, timer


class BaseAPIService:
    """Base class for API services with common functionality."""

    def __init__(self, base_url: str):
        """Initialize base service with URL."""
        self.base_url = base_url
        self.logger = get_logger(self.__class__.__name__)

    def _make_request(
        self,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request with common error handling.

        Args:
            params: Query parameters
            headers: Request headers

        Returns:
            JSON response data

        Raises:
            requests.RequestException: If request fails
        """
        with timer(self.logger, f"API request to {self.base_url}"):
            response = requests.get(
                self.base_url,
                params=params or {},
                headers=headers or {},
                timeout=API_TIMEOUT,
            )
            response.raise_for_status()

        with timer(self.logger, "JSON response parsing"):
            return response.json()
