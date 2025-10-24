"""
Kerykeion Calculator Adapter

Implements IAstrologicalCalculator using the Kerykeion library.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    from kerykeion import AstrologicalSubject, KerykeionChartSVG
    from kerykeion.aspects import AspectsFactory
    KERYKEION_AVAILABLE = True
except ImportError:
    KERYKEION_AVAILABLE = False
    AstrologicalSubject = None
    KerykeionChartSVG = None
    AspectsFactory = None

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
        # House system mapping: name -> Swiss Ephemeris letter code
        self.house_system_map = {
            "placidus": "P",
            "koch": "K",
            "equal": "A",
            "whole_sign": "W",
            "campanus": "C",
            "regiomontanus": "R",
            "topocentric": "T",
            "porphyry": "O",
            "morinus": "M",
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
            house_system_code = self.house_system_map.get(
                settings.DEFAULT_HOUSE_SYSTEM.lower(), "P"
            )
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
                houses_system_identifier=house_system_code,
            )

            # Extract planet positions
            planets = self._extract_planets(subject, include_chiron, include_lilith, include_nodes)

            # Extract houses
            houses = self._extract_houses(subject)

            # Calculate aspects
            aspects_model = AspectsFactory.single_chart_aspects(subject.model())
            aspects = self._extract_aspects(aspects_model.all_aspects)

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
        """Generate SVG representation of chart and save to file."""
        try:
            # Extract birth data from metadata if available
            metadata = chart_data.get("metadata", {})

            # This is a simplified implementation
            # In a full implementation, we would reconstruct the AstrologicalSubject
            # from chart_data and use KerykeionChartSVG

            output_file = Path(output_path) / f"chart_{datetime.utcnow().timestamp()}.svg"
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # For now, create a basic SVG placeholder
            # TODO: Implement full SVG generation using KerykeionChartSVG
            svg_content = self._generate_basic_svg(chart_data)
            output_file.write_text(svg_content)

            return str(output_file)

        except Exception as e:
            raise CalculationError(f"Failed to export chart SVG: {str(e)}", "export")

    def generate_chart_svg(
        self,
        birth_data: BirthData,
        chart_data: Dict[str, Any],
        chart_name: str = "Chart",
        language: str = "en"
    ) -> str:
        """Generate SVG representation of chart and return as string."""
        try:
            # Create astrological subject from birth data
            house_system_code = self.house_system_map.get(
                settings.DEFAULT_HOUSE_SYSTEM.lower(), "P"
            )
            subject = AstrologicalSubject(
                name=chart_name,
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
                houses_system_identifier=house_system_code,
            )

            # Generate SVG using KerykeionChartSVG
            lang_upper = language.upper() if language.upper() in ["EN", "ES", "IT", "FR", "DE", "PT"] else "EN"
            chart_svg = KerykeionChartSVG(
                subject,
                chart_type="Natal",
                chart_language=lang_upper,
            )

            # KerykeionChartSVG.makeSVG() generates a file and doesn't return content
            # We need to call it and then read the generated file
            chart_svg.makeSVG()

            # The SVG file is saved in the chart_svg output_directory
            # Kerykeion uses the subject's name with " - " separator
            # Example: "John Doe - Natal Chart.svg"
            svg_file_path = Path(chart_svg.output_directory) / f"{chart_name} - Natal Chart.svg"

            if svg_file_path.exists():
                svg_content = svg_file_path.read_text(encoding='utf-8')
                # Clean up the generated file
                svg_file_path.unlink()
                return svg_content
            else:
                # If file not found, fall back to basic SVG
                raise Exception(f"SVG file not generated at {svg_file_path}")

        except Exception as e:
            # If Kerykeion fails, return a basic SVG
            print(f"[ERROR] Failed to generate Kerykeion SVG: {str(e)}")
            print(f"[ERROR] Exception type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return self._generate_basic_svg(chart_data, chart_name)

    def _generate_basic_svg(
        self,
        chart_data: Dict[str, Any],
        chart_name: str = "Natal Chart"
    ) -> str:
        """
        Generate a basic SVG representation when full generation fails.

        This provides a fallback SVG with planet positions and basic chart info.
        """
        planets = chart_data.get("planets", [])
        houses = chart_data.get("houses", [])
        angles = chart_data.get("angles", {})

        # Extract key information
        sun = next((p for p in planets if p["name"] == "Sun"), None)
        moon = next((p for p in planets if p["name"] == "Moon"), None)
        ascendant = angles.get("ascendant", {})

        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 900" width="800" height="900">
  <style>
    .title {{ font: bold 24px sans-serif; fill: #333; }}
    .subtitle {{ font: 16px sans-serif; fill: #666; }}
    .planet {{ font: 14px sans-serif; fill: #444; }}
    .degree {{ font: 12px sans-serif; fill: #888; }}
    .circle {{ fill: none; stroke: #ddd; stroke-width: 2; }}
    .zodiac {{ fill: none; stroke: #aaa; stroke-width: 1; }}
  </style>

  <!-- Title -->
  <text x="400" y="40" text-anchor="middle" class="title">{chart_name}</text>
  <text x="400" y="65" text-anchor="middle" class="subtitle">Natal Chart</text>

  <!-- Main Chart Circle -->
  <circle cx="400" cy="450" r="280" class="circle"/>
  <circle cx="400" cy="450" r="240" class="zodiac"/>
  <circle cx="400" cy="450" r="200" class="zodiac"/>

  <!-- Zodiac Wheel (12 houses) -->'''

        # Draw 12 house divisions
        for i in range(12):
            angle = i * 30
            x1 = 400 + 200 * __import__('math').cos(__import__('math').radians(angle - 90))
            y1 = 450 + 200 * __import__('math').sin(__import__('math').radians(angle - 90))
            x2 = 400 + 280 * __import__('math').cos(__import__('math').radians(angle - 90))
            y2 = 450 + 280 * __import__('math').sin(__import__('math').radians(angle - 90))
            svg += f'\n  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="zodiac"/>'

        svg += '\n\n  <!-- Planet Positions -->'
        y_offset = 100
        for i, planet in enumerate(planets[:10]):  # First 10 planets
            y = y_offset + (i * 25)
            name = planet.get("name", "Unknown")
            sign = planet.get("sign", "")
            degree = planet.get("degree", 0)
            house = planet.get("house", 0)
            retrograde = " ℞" if planet.get("is_retrograde", False) else ""

            svg += f'''
  <text x="50" y="{y}" class="planet">{name}{retrograde}</text>
  <text x="200" y="{y}" class="degree">{sign} {degree:.2f}° (House {house})</text>'''

        # Add Ascendant info
        if ascendant:
            asc_sign = ascendant.get("sign", "")
            asc_degree = ascendant.get("degree", 0)
            svg += f'''

  <!-- Angles -->
  <text x="50" y="{y_offset + 275}" class="planet">Ascendant</text>
  <text x="200" y="{y_offset + 275}" class="degree">{asc_sign} {asc_degree:.2f}°</text>'''

        svg += '\n</svg>'

        return svg

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
                planet_obj = getattr(subject, planet_name)
                if planet_obj is None:
                    continue

                # Extract degree, minute, second from position
                position = getattr(planet_obj, 'position', 0.0)
                degree = int(position % 30)
                minute = int((position % 1) * 60)
                second = int(((position % 1) * 60 % 1) * 60)

                # Extract house number from house string (e.g., "Ninth_House" -> 9)
                house_str = getattr(planet_obj, 'house', '')
                house_num = 1
                house_map = {
                    'First_House': 1, 'Second_House': 2, 'Third_House': 3,
                    'Fourth_House': 4, 'Fifth_House': 5, 'Sixth_House': 6,
                    'Seventh_House': 7, 'Eighth_House': 8, 'Ninth_House': 9,
                    'Tenth_House': 10, 'Eleventh_House': 11, 'Twelfth_House': 12
                }
                house_num = house_map.get(house_str, 1)

                planets.append({
                    "name": planet_name.replace("_", " ").title(),
                    "longitude": position,
                    "latitude": 0.0,  # Not provided in kerykeion 5.x
                    "speed": getattr(planet_obj, 'speed', 0.0),
                    "sign": getattr(planet_obj, 'sign', ''),
                    "degree": degree,
                    "minute": minute,
                    "second": second,
                    "house": house_num,
                    "is_retrograde": getattr(planet_obj, 'retrograde', False),
                })

        return planets

    def _extract_houses(self, subject: AstrologicalSubject) -> List[Dict[str, Any]]:
        """Extract house positions from Kerykeion subject."""
        houses = []

        house_names = [
            "first_house", "second_house", "third_house", "fourth_house",
            "fifth_house", "sixth_house", "seventh_house", "eighth_house",
            "ninth_house", "tenth_house", "eleventh_house", "twelfth_house"
        ]

        for i, house_name in enumerate(house_names, start=1):
            if hasattr(subject, house_name):
                house_obj = getattr(subject, house_name)
                if house_obj is None:
                    continue

                position = getattr(house_obj, 'position', 0.0)
                degree = int(position % 30)

                houses.append({
                    "number": i,
                    "cusp_longitude": position,
                    "sign": getattr(house_obj, 'sign', ''),
                    "degree": degree,
                })

        return houses

    def _extract_aspects(self, aspects_list: List) -> List[Dict[str, Any]]:
        """Extract aspects from Kerykeion AspectsFactory result."""
        aspects = []

        for aspect in aspects_list:
            # Check if applying or separating
            is_applying = getattr(aspect, 'aspect_movement', '') == 'Applying'

            aspects.append({
                "planet1": getattr(aspect, 'p1_name', ''),
                "planet2": getattr(aspect, 'p2_name', ''),
                "aspect_type": getattr(aspect, 'aspect', '').lower(),
                "angle": getattr(aspect, 'aspect_degrees', 0.0),
                "orb": abs(getattr(aspect, 'orbit', 0.0)),
                "is_applying": is_applying,
            })

        return aspects

    def _extract_angles(self, subject: AstrologicalSubject) -> Dict[str, Any]:
        """Extract chart angles (ASC, MC, etc.) from Kerykeion subject."""
        angles = {}

        if hasattr(subject, "first_house") and subject.first_house:
            position = getattr(subject.first_house, 'position', 0.0)
            angles["ascendant"] = {
                "longitude": position,
                "sign": getattr(subject.first_house, 'sign', ''),
                "degree": int(position % 30),
            }

        if hasattr(subject, "tenth_house") and subject.tenth_house:
            position = getattr(subject.tenth_house, 'position', 0.0)
            angles["midheaven"] = {
                "longitude": position,
                "sign": getattr(subject.tenth_house, 'sign', ''),
                "degree": int(position % 30),
            }

        return angles
