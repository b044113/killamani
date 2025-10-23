"""
Value Object: CelestialPosition

Immutable value object representing a celestial body's position.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CelestialPosition:
    """
    Immutable position of a celestial body in the zodiac.

    Business Rules:
    - Longitude must be between 0 and 360 degrees
    - Latitude is between -90 and 90 degrees
    - Speed can be negative (retrograde)
    - Positions are immutable once created
    """
    name: str  # Planet/body name (e.g., "Sun", "Moon", "Mercury")
    longitude: float  # Absolute longitude (0-360 degrees)
    latitude: float  # Celestial latitude
    speed: float  # Daily motion in degrees (negative = retrograde)

    # Derived position info
    sign: str  # Zodiac sign (e.g., "Aries", "Taurus")
    degree: float  # Degree within sign (0-30)
    minute: int  # Minutes (0-59)
    second: int  # Seconds (0-59)

    # House placement
    house: int  # House number (1-12)

    # Optional attributes
    is_retrograde: bool = False
    dignity: Optional[str] = None  # domicile, exaltation, detriment, fall

    def __post_init__(self):
        """Validate value object after initialization"""
        if not 0 <= self.longitude < 360:
            raise ValueError("Longitude must be between 0 and 360 degrees")
        if not -90 <= self.latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90 degrees")
        if not 1 <= self.house <= 12:
            raise ValueError("House must be between 1 and 12")
        if not 0 <= self.degree < 30:
            raise ValueError("Degree must be between 0 and 30")
        if not 0 <= self.minute < 60:
            raise ValueError("Minute must be between 0 and 59")
        if not 0 <= self.second < 60:
            raise ValueError("Second must be between 0 and 59")

    @property
    def formatted_position(self) -> str:
        """Get formatted position string (e.g., '15°32'45" Aries')"""
        return f"{int(self.degree)}°{self.minute}'{self.second}\" {self.sign}"

    @property
    def retrograde_symbol(self) -> str:
        """Get retrograde symbol if applicable"""
        return "℞" if self.is_retrograde else ""

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "longitude": self.longitude,
            "latitude": self.latitude,
            "speed": self.speed,
            "sign": self.sign,
            "degree": self.degree,
            "minute": self.minute,
            "second": self.second,
            "house": self.house,
            "is_retrograde": self.is_retrograde,
            "dignity": self.dignity,
            "formatted_position": self.formatted_position,
        }

    def is_in_sign(self, sign: str) -> bool:
        """Check if position is in a specific sign"""
        return self.sign.lower() == sign.lower()

    def is_in_house(self, house: int) -> bool:
        """Check if position is in a specific house"""
        return self.house == house

    @staticmethod
    def calculate_sign(longitude: float) -> str:
        """Calculate zodiac sign from absolute longitude"""
        signs = [
            "Aries", "Taurus", "Gemini", "Cancer",
            "Leo", "Virgo", "Libra", "Scorpio",
            "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        sign_index = int(longitude / 30) % 12
        return signs[sign_index]

    @staticmethod
    def calculate_degree_in_sign(longitude: float) -> float:
        """Calculate degree within sign from absolute longitude"""
        return longitude % 30
