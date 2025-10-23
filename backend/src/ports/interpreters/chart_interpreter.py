"""
Port: ChartInterpreter

Interface for astrological chart interpretation.
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional

from ...domain.entities.natal_chart import NatalChart
from ...domain.entities.transit import Transit
from ...domain.entities.solar_return import SolarReturn


class IChartInterpreter(ABC):
    """
    Chart interpreter interface for generating interpretations.

    This is a port in hexagonal architecture - can be implemented
    with rule-based systems, AI models, or hybrid approaches.
    """

    @abstractmethod
    def interpret_natal_chart(
        self,
        chart: NatalChart,
        language: str = "en",
        detail_level: str = "standard"
    ) -> Dict[str, str]:
        """
        Generate interpretation for a natal chart.

        Args:
            chart: NatalChart entity
            language: Language code (es, en, it, fr, de, pt-br)
            detail_level: Level of detail (basic, standard, detailed)

        Returns:
            Dictionary of interpretations:
            {
                "sun_in_sign": "...",
                "sun_in_house": "...",
                "moon_in_sign": "...",
                "ascendant": "...",
                "aspects": {...},
                "overall": "..."
            }

        Raises:
            InterpretationError: If interpretation fails
            UnsupportedLanguageError: If language not supported
        """
        pass

    @abstractmethod
    def interpret_planet_in_sign(
        self,
        planet: str,
        sign: str,
        language: str = "en"
    ) -> str:
        """
        Interpret a planet in a specific sign.

        Args:
            planet: Planet name (e.g., "Sun", "Moon")
            sign: Zodiac sign (e.g., "Aries", "Taurus")
            language: Language code

        Returns:
            Interpretation text
        """
        pass

    @abstractmethod
    def interpret_planet_in_house(
        self,
        planet: str,
        house: int,
        language: str = "en"
    ) -> str:
        """
        Interpret a planet in a specific house.

        Args:
            planet: Planet name
            house: House number (1-12)
            language: Language code

        Returns:
            Interpretation text
        """
        pass

    @abstractmethod
    def interpret_aspect(
        self,
        planet1: str,
        planet2: str,
        aspect_type: str,
        language: str = "en"
    ) -> str:
        """
        Interpret an aspect between two planets.

        Args:
            planet1: First planet name
            planet2: Second planet name
            aspect_type: Aspect type (conjunction, opposition, etc.)
            language: Language code

        Returns:
            Interpretation text
        """
        pass

    @abstractmethod
    def interpret_solar_set(
        self,
        sun_sign: str,
        fifth_house_sign: str,
        hard_aspects: list,
        language: str = "en"
    ) -> str:
        """
        Interpret a solar set (Sun sign + 5th house + hard aspects).

        Args:
            sun_sign: Sun's zodiac sign
            fifth_house_sign: Sign on 5th house cusp
            hard_aspects: List of hard aspects to the Sun
            language: Language code

        Returns:
            Interpretation text
        """
        pass

    @abstractmethod
    def interpret_transit(
        self,
        transit: Transit,
        language: str = "en",
        detail_level: str = "standard"
    ) -> Dict[str, str]:
        """
        Generate interpretation for transits.

        Args:
            transit: Transit entity
            language: Language code
            detail_level: Level of detail

        Returns:
            Dictionary of transit interpretations
        """
        pass

    @abstractmethod
    def interpret_solar_return(
        self,
        solar_return: SolarReturn,
        language: str = "en",
        detail_level: str = "standard"
    ) -> Dict[str, str]:
        """
        Generate interpretation for solar return.

        Args:
            solar_return: SolarReturn entity
            language: Language code
            detail_level: Level of detail

        Returns:
            Dictionary of solar return interpretations
        """
        pass

    @abstractmethod
    def get_supported_languages(self) -> list[str]:
        """
        Get list of supported languages.

        Returns:
            List of language codes
        """
        pass

    @abstractmethod
    def is_language_supported(self, language: str) -> bool:
        """
        Check if a language is supported.

        Args:
            language: Language code

        Returns:
            True if supported, False otherwise
        """
        pass
