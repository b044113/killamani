"""
Chart DTOs (Data Transfer Objects)

Input/Output data structures for chart calculation use cases.
"""
from dataclasses import dataclass
from typing import Optional, Dict, List
from datetime import datetime


# ============================================================================
# Input DTOs
# ============================================================================

@dataclass
class CalculateNatalChartDTO:
    """Data required to calculate a natal chart."""
    client_id: str
    include_chiron: bool = True
    include_lilith: bool = True
    include_nodes: bool = True
    house_system: str = "placidus"
    language: str = "en"


@dataclass
class CalculateTransitsDTO:
    """Data required to calculate transits."""
    client_id: str
    natal_chart_id: str
    target_date: datetime
    language: str = "en"


@dataclass
class CalculateSolarReturnDTO:
    """Data required to calculate solar return."""
    client_id: str
    natal_chart_id: str
    return_year: int
    location_city: str
    location_country: str
    location_latitude: Optional[float] = None
    location_longitude: Optional[float] = None
    language: str = "en"


# ============================================================================
# Output DTOs
# ============================================================================

@dataclass
class NatalChartDTO:
    """Natal chart data returned to API consumers."""
    id: str
    client_id: str
    sun_sign: str
    planets: List[Dict]
    houses: List[Dict]
    aspects: List[Dict]
    angles: Dict
    solar_set: Dict
    interpretations: Dict[str, str]
    house_system: str
    svg_url: Optional[str]
    pdf_url: Optional[str]
    calculated_at: datetime
    created_at: datetime

    @classmethod
    def from_entity(cls, chart):
        """Create DTO from NatalChart entity."""
        return cls(
            id=str(chart.id),
            client_id=str(chart.client_id),
            sun_sign=chart.sun_sign,
            planets=chart.get_planets(),
            houses=chart.get_houses(),
            aspects=chart.get_aspects(),
            angles=chart.get_angles(),
            solar_set=chart.solar_set,
            interpretations=chart.interpretations,
            house_system=chart.house_system,
            svg_url=chart.svg_url,
            pdf_url=chart.pdf_url,
            calculated_at=chart.calculated_at,
            created_at=chart.created_at,
        )


@dataclass
class TransitDTO:
    """Transit data returned to API consumers."""
    id: str
    client_id: str
    natal_chart_id: str
    transit_date: datetime
    significant_aspects: List[Dict]
    active_transits: List[Dict]
    interpretations: Dict[str, str]
    calculated_at: datetime

    @classmethod
    def from_entity(cls, transit):
        """Create DTO from Transit entity."""
        return cls(
            id=str(transit.id),
            client_id=str(transit.client_id),
            natal_chart_id=str(transit.natal_chart_id),
            transit_date=transit.transit_date,
            significant_aspects=transit.significant_aspects,
            active_transits=transit.active_transits,
            interpretations=transit.interpretations,
            calculated_at=transit.calculated_at,
        )


@dataclass
class SolarReturnDTO:
    """Solar return data returned to API consumers."""
    id: str
    client_id: str
    natal_chart_id: str
    return_year: int
    return_datetime: datetime
    sun_sign: str
    planets: List[Dict]
    houses: List[Dict]
    aspects: List[Dict]
    solar_set: Dict
    interpretations: Dict[str, str]
    location_city: str
    location_country: str
    is_relocated: bool
    svg_url: Optional[str]
    pdf_url: Optional[str]
    calculated_at: datetime

    @classmethod
    def from_entity(cls, solar_return):
        """Create DTO from SolarReturn entity."""
        return cls(
            id=str(solar_return.id),
            client_id=str(solar_return.client_id),
            natal_chart_id=str(solar_return.natal_chart_id),
            return_year=solar_return.return_year,
            return_datetime=solar_return.return_datetime,
            sun_sign=solar_return.sun_sign,
            planets=solar_return.get_planets(),
            houses=solar_return.get_houses(),
            aspects=solar_return.get_aspects(),
            solar_set=solar_return.solar_set,
            interpretations=solar_return.interpretations,
            location_city=solar_return.location_city,
            location_country=solar_return.location_country,
            is_relocated=solar_return.is_relocated,
            svg_url=solar_return.svg_url,
            pdf_url=solar_return.pdf_url,
            calculated_at=solar_return.calculated_at,
        )
