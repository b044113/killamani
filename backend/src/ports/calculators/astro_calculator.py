"""
Port (Interface): Astrological Calculator

Defines the contract for any astrological calculation engine.
This allows us to swap Kerykeion for another library without changing business logic.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any
from uuid import UUID

from ...domain.value_objects.birth_data import BirthData


class IAstrologicalCalculator(ABC):
    """
    Interface for astrological calculations.

    Implementations: KerykeionCalculator, FlatlibCalculator, SwissEphemerisCalculator, etc.
    """

    @abstractmethod
    def calculate_natal_chart(
        self,
        birth_data: BirthData,
        include_chiron: bool = True,
        include_lilith: bool = True,
        include_nodes: bool = True,
    ) -> Dict[str, Any]:
        """
        Calculate natal chart.

        Returns:
            {
                "planets": [...],
                "houses": [...],
                "aspects": [...],
                "angles": {...},
                "metadata": {...}
            }
        """
        pass

    @abstractmethod
    def calculate_solar_set(
        self,
        natal_chart: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate Solar Set:
        - Sun sign
        - Sun house
        - 5th house sign
        - Hard aspects to Sun (conjunction, square, opposition)

        Returns:
            {
                "sun_sign": "Taurus",
                "sun_house": 12,
                "fifth_house_sign": "Virgo",
                "hard_aspects": [
                    {"planet": "Mars", "aspect": "square", "orb": 2.5},
                    ...
                ]
            }
        """
        pass

    @abstractmethod
    def calculate_transits(
        self,
        natal_chart: Dict[str, Any],
        target_date: datetime,
        orb_override: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Calculate transits for a specific date/time.

        Returns:
            {
                "date": "2025-10-22T14:00:00",
                "transits": [
                    {
                        "transiting_planet": "Jupiter",
                        "natal_planet": "Sun",
                        "aspect": "trine",
                        "orb": 1.2,
                        "is_applying": True
                    },
                    ...
                ]
            }
        """
        pass

    @abstractmethod
    def calculate_solar_return(
        self,
        birth_data: BirthData,
        return_year: int
    ) -> Dict[str, Any]:
        """
        Calculate Solar Return chart for a specific year.

        Returns:
            {
                "year": 2025,
                "return_date": "2025-04-24T12:34:56",
                "planets": [...],
                "houses": [...],
                "aspects": [...],
                "compared_to_natal": {
                    "aspects": [...]
                }
            }
        """
        pass

    @abstractmethod
    def export_chart_svg(
        self,
        chart_data: Dict[str, Any],
        output_path: str,
        language: str = "en"
    ) -> str:
        """
        Generate SVG representation of chart and save to file.

        Returns:
            Path to generated SVG file
        """
        pass

    @abstractmethod
    def generate_chart_svg(
        self,
        birth_data: BirthData,
        chart_data: Dict[str, Any],
        chart_name: str = "Chart",
        language: str = "en"
    ) -> str:
        """
        Generate SVG representation of chart and return as string.

        This method generates the SVG in-memory without saving to file,
        useful for quick chart calculations that don't require persistence.

        Returns:
            SVG content as string
        """
        pass

    @abstractmethod
    def get_supported_aspects(self) -> List[str]:
        """
        Get list of supported aspects.

        Returns:
            ["conjunction", "sextile", "square", "trine", "opposition",
             "semisquare", "sesquiquadrate", "quincunx"]
        """
        pass

    @abstractmethod
    def get_default_orbs(self) -> Dict[str, float]:
        """
        Get default orb values for aspects.

        Returns:
            {
                "conjunction": 8.0,
                "opposition": 8.0,
                "trine": 8.0,
                "square": 7.0,
                "sextile": 6.0,
                "semisquare": 3.0,
                "sesquiquadrate": 3.0,
                "quincunx": 3.0
            }
        """
        pass
