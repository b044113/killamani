"""
Value Object: Aspect

Immutable value object representing an astrological aspect between two celestial bodies.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class AspectType(str, Enum):
    """Traditional astrological aspects"""
    CONJUNCTION = "conjunction"  # 0° (union)
    OPPOSITION = "opposition"  # 180° (tension)
    TRINE = "trine"  # 120° (harmony)
    SQUARE = "square"  # 90° (challenge)
    SEXTILE = "sextile"  # 60° (opportunity)
    SEMISQUARE = "semisquare"  # 45° (minor tension)
    SESQUIQUADRATE = "sesquiquadrate"  # 135° (minor tension)
    QUINCUNX = "quincunx"  # 150° (adjustment)


class AspectQuality(str, Enum):
    """Aspect quality classification"""
    HARD = "hard"  # Challenging aspects (square, opposition)
    SOFT = "soft"  # Harmonious aspects (trine, sextile)
    NEUTRAL = "neutral"  # Conjunction
    MINOR = "minor"  # Minor aspects


@dataclass(frozen=True)
class Aspect:
    """
    Immutable aspect between two celestial bodies.

    Business Rules:
    - Must have two different celestial bodies
    - Aspect angle must match aspect type
    - Orb must be within allowed range for aspect type
    - Aspects are immutable once created
    """
    planet1: str  # First celestial body
    planet2: str  # Second celestial body
    aspect_type: AspectType  # Type of aspect
    angle: float  # Exact angle between bodies (0-180)
    orb: float  # Difference from exact aspect in degrees
    is_applying: bool = True  # True if aspect is forming, False if separating

    # Optional attributes
    quality: Optional[AspectQuality] = None
    strength: Optional[float] = None  # Aspect strength (0-1)

    def __post_init__(self):
        """Validate value object after initialization"""
        if self.planet1 == self.planet2:
            raise ValueError("Aspect must be between two different bodies")
        if not 0 <= self.angle <= 180:
            raise ValueError("Angle must be between 0 and 180 degrees")
        if self.orb < 0:
            raise ValueError("Orb cannot be negative")
        if self.strength is not None and not 0 <= self.strength <= 1:
            raise ValueError("Strength must be between 0 and 1")

    @property
    def is_hard_aspect(self) -> bool:
        """Check if this is a hard (challenging) aspect"""
        return self.aspect_type in [AspectType.SQUARE, AspectType.OPPOSITION]

    @property
    def is_soft_aspect(self) -> bool:
        """Check if this is a soft (harmonious) aspect"""
        return self.aspect_type in [AspectType.TRINE, AspectType.SEXTILE]

    @property
    def is_major_aspect(self) -> bool:
        """Check if this is a major aspect"""
        major_aspects = [
            AspectType.CONJUNCTION,
            AspectType.OPPOSITION,
            AspectType.TRINE,
            AspectType.SQUARE,
            AspectType.SEXTILE
        ]
        return self.aspect_type in major_aspects

    @property
    def is_minor_aspect(self) -> bool:
        """Check if this is a minor aspect"""
        return not self.is_major_aspect

    @property
    def symbol(self) -> str:
        """Get Unicode symbol for aspect"""
        symbols = {
            AspectType.CONJUNCTION: "☌",
            AspectType.OPPOSITION: "☍",
            AspectType.TRINE: "△",
            AspectType.SQUARE: "□",
            AspectType.SEXTILE: "⚹",
            AspectType.SEMISQUARE: "∠",
            AspectType.SESQUIQUADRATE: "⚼",
            AspectType.QUINCUNX: "⚻",
        }
        return symbols.get(self.aspect_type, "")

    @property
    def exact_angle(self) -> float:
        """Get the exact angle for this aspect type"""
        angles = {
            AspectType.CONJUNCTION: 0.0,
            AspectType.OPPOSITION: 180.0,
            AspectType.TRINE: 120.0,
            AspectType.SQUARE: 90.0,
            AspectType.SEXTILE: 60.0,
            AspectType.SEMISQUARE: 45.0,
            AspectType.SESQUIQUADRATE: 135.0,
            AspectType.QUINCUNX: 150.0,
        }
        return angles.get(self.aspect_type, 0.0)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "planet1": self.planet1,
            "planet2": self.planet2,
            "aspect_type": self.aspect_type.value,
            "angle": self.angle,
            "orb": self.orb,
            "is_applying": self.is_applying,
            "quality": self.quality.value if self.quality else None,
            "strength": self.strength,
            "symbol": self.symbol,
            "is_hard": self.is_hard_aspect,
            "is_soft": self.is_soft_aspect,
            "is_major": self.is_major_aspect,
        }

    def involves_planet(self, planet_name: str) -> bool:
        """Check if aspect involves a specific planet"""
        return planet_name in [self.planet1, self.planet2]

    @staticmethod
    def get_default_orb(aspect_type: AspectType) -> float:
        """Get default orb for aspect type"""
        orbs = {
            AspectType.CONJUNCTION: 8.0,
            AspectType.OPPOSITION: 8.0,
            AspectType.TRINE: 8.0,
            AspectType.SQUARE: 7.0,
            AspectType.SEXTILE: 6.0,
            AspectType.SEMISQUARE: 3.0,
            AspectType.SESQUIQUADRATE: 3.0,
            AspectType.QUINCUNX: 3.0,
        }
        return orbs.get(aspect_type, 1.0)

    @staticmethod
    def determine_quality(aspect_type: AspectType) -> AspectQuality:
        """Determine quality of aspect based on type"""
        if aspect_type in [AspectType.SQUARE, AspectType.OPPOSITION]:
            return AspectQuality.HARD
        elif aspect_type in [AspectType.TRINE, AspectType.SEXTILE]:
            return AspectQuality.SOFT
        elif aspect_type == AspectType.CONJUNCTION:
            return AspectQuality.NEUTRAL
        else:
            return AspectQuality.MINOR
