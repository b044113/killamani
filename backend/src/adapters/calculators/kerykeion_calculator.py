"""
Kerykeion Calculator Adapter

Implements IAstrologicalCalculator using the Kerykeion library.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    from kerykeion import AstrologicalSubject, KerykeionChartSVG
    from kerykeion.aspects import NatalAspects
    KERYKEION_AVAILABLE = True
except ImportError:
    KERYKEION_AVAILABLE = False
    AstrologicalSubject = None
    KerykeionChartSVG = None
    NatalAspects = None

from ...domain.value_objects.birth_data import BirthData
from ...domain.exceptions import CalculationError
from ...ports.calculators.astro_calculator import IAstrologicalCalculator
from ...infrastructure.config.settings import get_settings

settings = get_settings()


class KerykeionCalculator(IAstrologicalCalculator):
    """
    Kerykeion-based implementation of astrological calculator.

    Uses the Kerykeion library for all astronomical calculations.
    """

    def __init__(self):
        if not KERYKEION_AVAILABLE:
            raise ImportError(
                "Kerykeion library is not installed. "
                "Install it with: pip install kerykeion==5.0.2\n"
                "Note: On Windows, this requires Microsoft C++ Build Tools."
            )
        self.default_orbs = {
            "conjunction": settings.ORB_CONJUNCTION,
            "opposition": settings.ORB_OPPOSITION,
            "trine": settings.ORB_TRINE,
            "square": settings.ORB_SQUARE,
            "sextile": settings.ORB_SEXTILE,
            "semisquare": settings.ORB_SEMISQUARE,
            "sesquiquadrate": settings.ORB_SESQUIQUADRATE,
            "quincunx": settings.ORB_QUINCUNX,
        }

    def calculate_natal_chart(
        self,
        birth_data: BirthData,
        include_chiron: bool = True,
        include_lilith: bool = True,
        include_nodes: bool = True,
    ) -> Dict[str, Any]:
        """Calculate natal chart using Kerykeion."""
        try:
            # Create astrological subject
            subject = AstrologicalSubject(
                name="Chart",
                year=birth_data.date.year,
                month=birth_data.date.month,
                day=birth_data.date.day,
                hour=birth_data.date.hour,
                minute=birth_data.date.minute,
                city=birth_data.city,
                nation=birth_data.country,
                lat=birth_data.latitude,
                lng=birth_data.longitude,
                tz_str=birth_data.timezone,
                zodiac_type="Tropic",
                sidereal_mode=None,
                house_system=settings.DEFAULT_HOUSE_SYSTEM.capitalize(),
            )

            # Extract planet positions
            planets = self._extract_planets(subject, include_chiron, include_lilith, include_nodes)

            # Extract houses
            houses = self._extract_houses(subject)

            # Calculate aspects
            natal_aspects = NatalAspects(subject)
            aspects = self._extract_aspects(natal_aspects)

            # Extract angles
            angles = self._extract_angles(subject)

            return {
                "planets": planets,
                "houses": houses,
                "aspects": aspects,
                "angles": angles,
                "metadata": {
                    "house_system": settings.DEFAULT_HOUSE_SYSTEM,
                    "zodiac_type": "tropical",
                    "calculated_at": datetime.utcnow().isoformat(),
                }
            }

        except Exception as e:
            raise CalculationError(f"Failed to calculate natal chart: {str(e)}", "natal_chart")

    def calculate_solar_set(self, natal_chart: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Solar Set from natal chart data."""
        try:
            # Find Sun
            sun = next((p for p in natal_chart["planets"] if p["name"] == "Sun"), None)
            if not sun:
                raise CalculationError("Sun not found in chart data", "solar_set")

            # Find 5th house
            houses = natal_chart.get("houses", [])
            if len(houses) < 5:
                raise CalculationError("5th house not found in chart data", "solar_set")

            fifth_house = houses[4]  # 5th house (0-indexed)

            # Filter hard aspects to Sun
            all_aspects = natal_chart.get("aspects", [])
            hard_aspects = [
                {
                    "planet": a["planet2"] if a["planet1"] == "Sun" else a["planet1"],
                    "aspect": a["aspect_type"],
                    "orb": a["orb"],
                }
                for a in all_aspects
                if "Sun" in [a["planet1"], a["planet2"]]
                and a["aspect_type"] in ["conjunction", "square", "opposition"]
            ]

            return {
                "sun_sign": sun["sign"],
                "sun_house": sun["house"],
                "sun_degree": sun["degree"],
                "fifth_house_sign": fifth_house["sign"],
                "hard_aspects": hard_aspects,
            }

        except Exception as e:
            raise CalculationError(f"Failed to calculate solar set: {str(e)}", "solar_set")

    def calculate_transits(
        self,
        natal_chart: Dict[str, Any],
        target_date: datetime,
        orb_override: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """Calculate transits for a specific date."""
        try:
            # TODO: Implement transit calculation with Kerykeion
            # This is a simplified version - full implementation would compare
            # transiting planet positions with natal positions

            orbs = orb_override or self.default_orbs

            return {
                "date": target_date.isoformat(),
                "transits": [],
                "metadata": {
                    "orbs_used": orbs,
                    "calculated_at": datetime.utcnow().isoformat(),
                }
            }

        except Exception as e:
            raise CalculationError(f"Failed to calculate transits: {str(e)}", "transit")

    def calculate_solar_return(
        self,
        birth_data: BirthData,
        return_year: int
    ) -> Dict[str, Any]:
        """Calculate Solar Return chart for a specific year."""
        try:
            # TODO: Implement solar return calculation
            # This requires finding the exact moment when the Sun returns
            # to its natal position in the specified year

            return {
                "year": return_year,
                "return_date": None,
                "planets": [],
                "houses": [],
                "aspects": [],
                "metadata": {
                    "calculated_at": datetime.utcnow().isoformat(),
                }
            }

        except Exception as e:
            raise CalculationError(f"Failed to calculate solar return: {str(e)}", "solar_return")

    def export_chart_svg(
        self,
        chart_data: Dict[str, Any],
        output_path: str,
        language: str = "en"
    ) -> str:
        """Generate SVG representation of chart."""
        try:
            # TODO: Implement SVG export using KerykeionChartSVG
            # This requires reconstructing an AstrologicalSubject from chart_data

            output_file = Path(output_path) / f"chart_{datetime.utcnow().timestamp()}.svg"
            return str(output_file)

        except Exception as e:
            raise CalculationError(f"Failed to export chart SVG: {str(e)}", "export")

    def get_supported_aspects(self) -> List[str]:
        """Get list of supported aspects."""
        return [
            "conjunction",
            "sextile",
            "square",
            "trine",
            "opposition",
            "semisquare",
            "sesquiquadrate",
            "quincunx",
        ]

    def get_default_orbs(self) -> Dict[str, float]:
        """Get default orb values for aspects."""
        return self.default_orbs.copy()

    # ========================================================================
    # Private Helper Methods
    # ========================================================================

    def _extract_planets(
        self,
        subject: AstrologicalSubject,
        include_chiron: bool,
        include_lilith: bool,
        include_nodes: bool
    ) -> List[Dict[str, Any]]:
        """Extract planet positions from Kerykeion subject."""
        planets = []

        # Standard planets
        planet_names = [
            "sun", "moon", "mercury", "venus", "mars",
            "jupiter", "saturn", "uranus", "neptune", "pluto"
        ]

        if include_chiron:
            planet_names.append("chiron")

        if include_lilith:
            planet_names.append("mean_lilith")

        if include_nodes:
            planet_names.extend(["mean_node", "true_node"])

        for planet_name in planet_names:
            if hasattr(subject, planet_name):
                planet_data = getattr(subject, planet_name)
                planets.append({
                    "name": planet_name.replace("_", " ").title(),
                    "longitude": planet_data.get("position", 0.0),
                    "latitude": planet_data.get("latitude", 0.0),
                    "speed": planet_data.get("speed", 0.0),
                    "sign": planet_data.get("sign", ""),
                    "degree": planet_data.get("pos_degree", 0.0),
                    "minute": int(planet_data.get("pos_minute", 0)),
                    "second": int(planet_data.get("pos_second", 0)),
                    "house": planet_data.get("house", 1),
                    "is_retrograde": planet_data.get("retrograde", False),
                })

        return planets

    def _extract_houses(self, subject: AstrologicalSubject) -> List[Dict[str, Any]]:
        """Extract house positions from Kerykeion subject."""
        houses = []

        for i in range(1, 13):
            house_attr = f"first_house" if i == 1 else f"house{i}"
            if hasattr(subject, house_attr):
                house_data = getattr(subject, house_attr)
                houses.append({
                    "number": i,
                    "cusp_longitude": house_data.get("position", 0.0),
                    "sign": house_data.get("sign", ""),
                    "degree": house_data.get("pos_degree", 0.0),
                })

        return houses

    def _extract_aspects(self, natal_aspects: NatalAspects) -> List[Dict[str, Any]]:
        """Extract aspects from Kerykeion NatalAspects."""
        aspects = []

        if hasattr(natal_aspects, "all_aspects"):
            for aspect in natal_aspects.all_aspects:
                aspects.append({
                    "planet1": aspect.get("p1_name", ""),
                    "planet2": aspect.get("p2_name", ""),
                    "aspect_type": aspect.get("aspect", "").lower(),
                    "angle": aspect.get("orbit", 0.0),
                    "orb": abs(aspect.get("orbit", 0.0) - aspect.get("aspect_degrees", 0.0)),
                    "is_applying": aspect.get("aid", 0) > 0,
                })

        return aspects

    def _extract_angles(self, subject: AstrologicalSubject) -> Dict[str, Any]:
        """Extract chart angles (ASC, MC, etc.) from Kerykeion subject."""
        angles = {}

        if hasattr(subject, "first_house"):
            angles["ascendant"] = {
                "longitude": subject.first_house.get("position", 0.0),
                "sign": subject.first_house.get("sign", ""),
                "degree": subject.first_house.get("pos_degree", 0.0),
            }

        if hasattr(subject, "tenth_house"):
            angles["midheaven"] = {
                "longitude": subject.tenth_house.get("position", 0.0),
                "sign": subject.tenth_house.get("sign", ""),
                "degree": subject.tenth_house.get("pos_degree", 0.0),
            }

        return angles
