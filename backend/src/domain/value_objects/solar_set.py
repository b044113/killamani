"""
Value Object: SolarSet

Immutable value object representing the Solar Set (Sun sign, 5th house, hard aspects).
"""
from dataclasses import dataclass
from typing import List, Dict


@dataclass(frozen=True)
class SolarSet:
    """
    Immutable Solar Set calculation.

    The Solar Set consists of:
    1. Sun's zodiac sign
    2. Sun's house position
    3. 5th house sign
    4. Hard aspects to the Sun (conjunction, square, opposition)

    Business Rules:
    - Sun sign must be valid zodiac sign
    - Houses must be 1-12
    - Hard aspects only include conjunction, square, opposition
    - Solar Set is immutable once calculated
    """
    sun_sign: str  # Sun's zodiac sign
    sun_house: int  # House where Sun is located (1-12)
    sun_degree: float  # Exact degree of Sun in sign
    fifth_house_sign: str  # Sign on the cusp of the 5th house
    hard_aspects: List[Dict]  # Hard aspects to the Sun

    def __post_init__(self):
        """Validate value object after initialization"""
        valid_signs = [
            "Aries", "Taurus", "Gemini", "Cancer",
            "Leo", "Virgo", "Libra", "Scorpio",
            "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]

        if self.sun_sign not in valid_signs:
            raise ValueError(f"Invalid sun sign: {self.sun_sign}")
        if self.fifth_house_sign not in valid_signs:
            raise ValueError(f"Invalid 5th house sign: {self.fifth_house_sign}")
        if not 1 <= self.sun_house <= 12:
            raise ValueError("Sun house must be between 1 and 12")
        if not 0 <= self.sun_degree < 30:
            raise ValueError("Sun degree must be between 0 and 30")

        # Validate hard aspects
        valid_aspect_types = ["conjunction", "square", "opposition"]
        for aspect in self.hard_aspects:
            if "aspect_type" not in aspect:
                raise ValueError("Aspect must have aspect_type field")
            if aspect["aspect_type"] not in valid_aspect_types:
                raise ValueError(f"Only hard aspects allowed, got: {aspect['aspect_type']}")

    @property
    def has_hard_aspects(self) -> bool:
        """Check if Sun has any hard aspects"""
        return len(self.hard_aspects) > 0

    @property
    def aspect_count(self) -> int:
        """Get count of hard aspects to the Sun"""
        return len(self.hard_aspects)

    def get_conjunctions(self) -> List[Dict]:
        """Get all conjunctions to the Sun"""
        return [a for a in self.hard_aspects if a["aspect_type"] == "conjunction"]

    def get_squares(self) -> List[Dict]:
        """Get all squares to the Sun"""
        return [a for a in self.hard_aspects if a["aspect_type"] == "square"]

    def get_oppositions(self) -> List[Dict]:
        """Get all oppositions to the Sun"""
        return [a for a in self.hard_aspects if a["aspect_type"] == "opposition"]

    def has_aspect_to_planet(self, planet_name: str) -> bool:
        """Check if Sun has hard aspect to specific planet"""
        return any(
            aspect.get("planet2") == planet_name or aspect.get("planet1") == planet_name
            for aspect in self.hard_aspects
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "sun_sign": self.sun_sign,
            "sun_house": self.sun_house,
            "sun_degree": self.sun_degree,
            "fifth_house_sign": self.fifth_house_sign,
            "hard_aspects": self.hard_aspects,
            "aspect_count": self.aspect_count,
            "has_hard_aspects": self.has_hard_aspects,
        }

    @property
    def formatted_sun_position(self) -> str:
        """Get formatted sun position string"""
        return f"{int(self.sun_degree)}° {self.sun_sign} in {self.sun_house}th house"

    @property
    def interpretation_key(self) -> str:
        """Get unique key for interpretation lookup"""
        # Format: SunSign_5thHouseSign_AspectCount
        return f"{self.sun_sign}_{self.fifth_house_sign}_{self.aspect_count}"

    def get_aspect_summary(self) -> Dict[str, int]:
        """Get summary of aspect types"""
        return {
            "conjunctions": len(self.get_conjunctions()),
            "squares": len(self.get_squares()),
            "oppositions": len(self.get_oppositions()),
            "total": self.aspect_count,
        }

    @staticmethod
    def from_chart_data(chart_data: Dict) -> 'SolarSet':
        """
        Create SolarSet from raw chart data.

        Args:
            chart_data: Dictionary containing planets, houses, and aspects

        Returns:
            SolarSet instance
        """
        # Find Sun position
        sun = next((p for p in chart_data.get("planets", []) if p["name"] == "Sun"), None)
        if not sun:
            raise ValueError("Sun position not found in chart data")

        # Find 5th house
        houses = chart_data.get("houses", [])
        if len(houses) < 5:
            raise ValueError("5th house not found in chart data")
        fifth_house = houses[4]  # 5th house (0-indexed)

        # Filter hard aspects to Sun
        all_aspects = chart_data.get("aspects", [])
        hard_aspects = [
            a for a in all_aspects
            if ("Sun" in [a.get("planet1"), a.get("planet2")])
            and a.get("aspect_type") in ["conjunction", "square", "opposition"]
        ]

        return SolarSet(
            sun_sign=sun["sign"],
            sun_house=sun["house"],
            sun_degree=sun["degree"],
            fifth_house_sign=fifth_house["sign"],
            hard_aspects=hard_aspects,
        )
