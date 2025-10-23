"""
Rule-Based Chart Interpreter Adapter

Implements IChartInterpreter using pre-defined interpretation rules.
"""
from typing import Dict
import json
from pathlib import Path

from ...domain.entities.natal_chart import NatalChart
from ...domain.entities.transit import Transit
from ...domain.entities.solar_return import SolarReturn
from ...domain.exceptions import InterpretationError, UnsupportedLanguageError
from ...ports.interpreters.chart_interpreter import IChartInterpreter


class RuleBasedInterpreter(IChartInterpreter):
    """
    Rule-based implementation of chart interpreter.

    Uses pre-defined interpretation templates stored in JSON files.
    Supports multiple languages and detail levels.
    """

    SUPPORTED_LANGUAGES = ["es", "en", "it", "fr", "de", "pt-br"]

    def __init__(self, translations_path: str = None):
        """
        Initialize rule-based interpreter.

        Args:
            translations_path: Path to translations directory
        """
        if translations_path:
            self.translations_path = Path(translations_path)
        else:
            self.translations_path = Path(__file__).parent / "translations"

        self._translations = {}
        self._load_translations()

    def _load_translations(self):
        """Load all translation files."""
        for lang in self.SUPPORTED_LANGUAGES:
            file_path = self.translations_path / f"{lang}.json"
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    self._translations[lang] = json.load(f)
            else:
                # Create basic structure if file doesn't exist
                self._translations[lang] = self._get_default_translations()

    def _get_default_translations(self) -> Dict:
        """Get default English translations as fallback."""
        return {
            "planets_in_signs": {},
            "planets_in_houses": {},
            "aspects": {},
            "solar_sets": {},
            "general": {
                "interpretation_unavailable": "Interpretation not available for this combination."
            }
        }

    def interpret_natal_chart(
        self,
        chart: NatalChart,
        language: str = "en",
        detail_level: str = "standard"
    ) -> Dict[str, str]:
        """Generate interpretation for a natal chart."""
        if not self.is_language_supported(language):
            raise UnsupportedLanguageError(language)

        try:
            translations = self._translations.get(language, self._translations["en"])
            interpretations = {}

            # Interpret planets in signs
            for planet in chart.get_planets():
                planet_name = planet["name"]
                sign = planet["sign"]
                house = planet["house"]

                # Planet in sign
                sign_key = f"{planet_name.lower()}_in_{sign.lower()}"
                interpretations[f"{planet_name}_in_sign"] = translations["planets_in_signs"].get(
                    sign_key,
                    f"{planet_name} in {sign}"
                )

                # Planet in house
                house_key = f"{planet_name.lower()}_in_house_{house}"
                interpretations[f"{planet_name}_in_house"] = translations["planets_in_houses"].get(
                    house_key,
                    f"{planet_name} in house {house}"
                )

            # Interpret aspects
            aspect_interpretations = []
            for aspect in chart.get_aspects():
                aspect_key = f"{aspect['planet1'].lower()}_{aspect['aspect_type']}_{aspect['planet2'].lower()}"
                interpretation = translations["aspects"].get(
                    aspect_key,
                    f"{aspect['planet1']} {aspect['aspect_type']} {aspect['planet2']}"
                )
                aspect_interpretations.append(interpretation)

            interpretations["aspects"] = " ".join(aspect_interpretations)

            # Interpret solar set
            solar_set_key = f"{chart.sun_sign.lower()}_solar_set"
            interpretations["solar_set"] = translations["solar_sets"].get(
                solar_set_key,
                f"Solar set in {chart.sun_sign}"
            )

            # Overall interpretation
            interpretations["overall"] = self._generate_overall_interpretation(
                chart,
                translations,
                detail_level
            )

            return interpretations

        except Exception as e:
            raise InterpretationError(f"Failed to interpret natal chart: {str(e)}", language)

    def interpret_planet_in_sign(
        self,
        planet: str,
        sign: str,
        language: str = "en"
    ) -> str:
        """Interpret a planet in a specific sign."""
        if not self.is_language_supported(language):
            raise UnsupportedLanguageError(language)

        translations = self._translations.get(language, self._translations["en"])
        key = f"{planet.lower()}_in_{sign.lower()}"

        return translations["planets_in_signs"].get(
            key,
            translations["general"]["interpretation_unavailable"]
        )

    def interpret_planet_in_house(
        self,
        planet: str,
        house: int,
        language: str = "en"
    ) -> str:
        """Interpret a planet in a specific house."""
        if not self.is_language_supported(language):
            raise UnsupportedLanguageError(language)

        translations = self._translations.get(language, self._translations["en"])
        key = f"{planet.lower()}_in_house_{house}"

        return translations["planets_in_houses"].get(
            key,
            translations["general"]["interpretation_unavailable"]
        )

    def interpret_aspect(
        self,
        planet1: str,
        planet2: str,
        aspect_type: str,
        language: str = "en"
    ) -> str:
        """Interpret an aspect between two planets."""
        if not self.is_language_supported(language):
            raise UnsupportedLanguageError(language)

        translations = self._translations.get(language, self._translations["en"])
        key = f"{planet1.lower()}_{aspect_type.lower()}_{planet2.lower()}"

        return translations["aspects"].get(
            key,
            translations["general"]["interpretation_unavailable"]
        )

    def interpret_solar_set(
        self,
        sun_sign: str,
        fifth_house_sign: str,
        hard_aspects: list,
        language: str = "en"
    ) -> str:
        """Interpret a solar set."""
        if not self.is_language_supported(language):
            raise UnsupportedLanguageError(language)

        translations = self._translations.get(language, self._translations["en"])
        key = f"{sun_sign.lower()}_solar_set"

        base_interpretation = translations["solar_sets"].get(
            key,
            f"Solar set with Sun in {sun_sign}"
        )

        # Add information about hard aspects
        if hard_aspects:
            aspect_count = len(hard_aspects)
            if language == "es":
                base_interpretation += f" Con {aspect_count} aspectos duros al Sol."
            else:
                base_interpretation += f" With {aspect_count} hard aspects to the Sun."

        return base_interpretation

    def interpret_transit(
        self,
        transit: Transit,
        language: str = "en",
        detail_level: str = "standard"
    ) -> Dict[str, str]:
        """Generate interpretation for transits."""
        if not self.is_language_supported(language):
            raise UnsupportedLanguageError(language)

        try:
            translations = self._translations.get(language, self._translations["en"])
            interpretations = {}

            # Interpret significant aspects
            for aspect in transit.significant_aspects:
                aspect_key = f"transit_{aspect['transiting_planet'].lower()}_{aspect['aspect_type']}_{aspect['natal_planet'].lower()}"
                interpretations[aspect_key] = translations["aspects"].get(
                    aspect_key,
                    f"Transit {aspect['transiting_planet']} {aspect['aspect_type']} natal {aspect['natal_planet']}"
                )

            # Overall transit interpretation
            interpretations["overall"] = self._generate_transit_overview(
                transit,
                translations,
                detail_level
            )

            return interpretations

        except Exception as e:
            raise InterpretationError(f"Failed to interpret transit: {str(e)}", language)

    def interpret_solar_return(
        self,
        solar_return: SolarReturn,
        language: str = "en",
        detail_level: str = "standard"
    ) -> Dict[str, str]:
        """Generate interpretation for solar return."""
        if not self.is_language_supported(language):
            raise UnsupportedLanguageError(language)

        try:
            translations = self._translations.get(language, self._translations["en"])
            interpretations = {}

            # Similar to natal chart interpretation but for solar return
            for planet in solar_return.get_planets():
                planet_name = planet["name"]
                sign = planet["sign"]

                sign_key = f"sr_{planet_name.lower()}_in_{sign.lower()}"
                interpretations[f"{planet_name}_in_sign"] = translations["planets_in_signs"].get(
                    sign_key,
                    f"Solar Return: {planet_name} in {sign}"
                )

            # Overall interpretation
            interpretations["overall"] = self._generate_solar_return_overview(
                solar_return,
                translations,
                detail_level
            )

            return interpretations

        except Exception as e:
            raise InterpretationError(f"Failed to interpret solar return: {str(e)}", language)

    def get_supported_languages(self) -> list[str]:
        """Get list of supported languages."""
        return self.SUPPORTED_LANGUAGES.copy()

    def is_language_supported(self, language: str) -> bool:
        """Check if a language is supported."""
        return language in self.SUPPORTED_LANGUAGES

    # ========================================================================
    # Private Helper Methods
    # ========================================================================

    def _generate_overall_interpretation(
        self,
        chart: NatalChart,
        translations: Dict,
        detail_level: str
    ) -> str:
        """Generate overall chart interpretation."""
        # Basic overall interpretation combining key factors
        sun_sign = chart.sun_sign
        ascendant = chart.get_angles().get("ascendant", {}).get("sign", "Unknown")

        if detail_level == "basic":
            return f"Sun in {sun_sign}, Ascendant in {ascendant}."
        elif detail_level == "detailed":
            aspects_count = len(chart.get_aspects())
            return f"Sun in {sun_sign}, Ascendant in {ascendant}. Chart contains {aspects_count} aspects."
        else:  # standard
            return f"Sun in {sun_sign} with Ascendant in {ascendant}."

    def _generate_transit_overview(
        self,
        transit: Transit,
        translations: Dict,
        detail_level: str
    ) -> str:
        """Generate overall transit interpretation."""
        aspect_count = transit.aspect_count
        date = transit.transit_date.strftime("%Y-%m-%d")

        return f"Transit for {date} with {aspect_count} significant aspects."

    def _generate_solar_return_overview(
        self,
        solar_return: SolarReturn,
        translations: Dict,
        detail_level: str
    ) -> str:
        """Generate overall solar return interpretation."""
        year = solar_return.return_year
        sun_sign = solar_return.sun_sign

        return f"Solar Return {year}: Sun in {sun_sign}."
