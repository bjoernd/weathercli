"""Common types and dataclasses for the weather application."""

from dataclasses import dataclass
from typing import Tuple, Union


@dataclass
class Location:
    """Represents a location for weather lookup."""

    value: Union[str, Tuple[float, float]]
    description: str

    @classmethod
    def from_city(cls, city: str) -> "Location":
        """Create location from city name."""
        return cls(value=city, description=f"city {city}")

    @classmethod
    def from_coordinates(cls, lat: float, lon: float) -> "Location":
        """Create location from coordinates."""
        return cls(
            value=(lat, lon), description=f"coordinates {lat:.2f}, {lon:.2f}"
        )

    @property
    def is_coordinates(self) -> bool:
        """Check if location uses coordinates."""
        return isinstance(self.value, tuple)

    @property
    def coordinates(self) -> Tuple[float, float]:
        """Get coordinates, raising error if not coordinate-based."""
        if not self.is_coordinates:
            raise ValueError("Location is not coordinate-based")
        return self.value  # type: ignore

    @property
    def city_name(self) -> str:
        """Get city name, raising error if not city-based."""
        if self.is_coordinates:
            raise ValueError("Location is not city-based")
        return self.value  # type: ignore
