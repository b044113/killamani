"""
Value Object: BirthData

Immutable value object representing birth information for chart calculation.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class BirthData:
    """
    Immutable birth data for astrological calculations.

    Business Rules:
    - Date and time are required
    - Location must be specified (city/country OR lat/lon)
    - Once created, cannot be modified (immutable)
    """
    date: datetime  # Birth date and time
    city: str
    country: str  # ISO country code (e.g., "AR", "US")
    timezone: str  # IANA timezone (e.g., "America/Argentina/Buenos_Aires")

    # Optional: Manual coordinates (override city lookup)
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    def __post_init__(self):
        """Validate value object after initialization"""
        if not self.date:
            raise ValueError("Birth date is required")
        if not self.city:
            raise ValueError("City is required")
        if not self.country:
            raise ValueError("Country is required")
        if not self.timezone:
            raise ValueError("Timezone is required")

        # Validate coordinates if provided
        if self.latitude is not None:
            if not -90 <= self.latitude <= 90:
                raise ValueError("Latitude must be between -90 and 90")
        if self.longitude is not None:
            if not -180 <= self.longitude <= 180:
                raise ValueError("Longitude must be between -180 and 180")

    @property
    def has_coordinates(self) -> bool:
        """Check if manual coordinates are provided"""
        return self.latitude is not None and self.longitude is not None

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "date": self.date.isoformat(),
            "city": self.city,
            "country": self.country,
            "timezone": self.timezone,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }
