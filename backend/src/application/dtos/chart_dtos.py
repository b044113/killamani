"""
Chart DTOs (Data Transfer Objects)

Input/Output data structures for chart calculation use cases.
All DTOs use Pydantic with camelCase aliases for frontend compatibility.
"""
from typing import Optional, Dict, List
from datetime import datetime
from pydantic import BaseModel, Field


# ============================================================================
# Input DTOs
# ============================================================================

class CreateChartForClientDTO(BaseModel):
    """
    Data required to create a natal chart for an existing client.

    Similar to QuickCalculateChartDTO but saves the chart to the database
    and associates it with a client.
    """
    name: str = Field(..., description="Name for this chart (e.g., 'Birth Chart', 'Rectified Chart')")
    birth_date: str = Field(..., description="ISO format: YYYY-MM-DD")
    birth_time: str = Field(..., description="HH:MM format: 14:30")
    birth_city: str
    birth_country: str = Field(..., description="ISO code: US, AR, etc.")
    birth_timezone: str = Field(..., description="IANA timezone: America/New_York")
    birth_latitude: Optional[float] = None
    birth_longitude: Optional[float] = None
    include_chiron: bool = True
    include_lilith: bool = True
    include_nodes: bool = True
    house_system: str = "placidus"
    language: str = "en"

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Birth Chart",
                "birth_date": "1990-05-15",
                "birth_time": "14:30",
                "birth_city": "Buenos Aires",
                "birth_country": "AR",
                "birth_timezone": "America/Argentina/Buenos_Aires",
                "include_chiron": True,
                "include_lilith": True,
                "include_nodes": True,
                "house_system": "placidus",
                "language": "en"
            }
        }


class CalculateNatalChartDTO(BaseModel):
    """Data required to calculate a natal chart."""
    client_id: str = Field(..., alias='clientId')
    include_chiron: bool = Field(True, alias='includeChiron')
    include_lilith: bool = Field(True, alias='includeLilith')
    include_nodes: bool = Field(True, alias='includeNodes')
    house_system: str = Field("placidus", alias='houseSystem')
    language: str = "en"

    class Config:
        populate_by_name = True


class CalculateTransitsDTO(BaseModel):
    """Data required to calculate transits."""
    client_id: str = Field(..., alias='clientId')
    natal_chart_id: str = Field(..., alias='natalChartId')
    target_date: datetime = Field(..., alias='targetDate')
    language: str = "en"

    class Config:
        populate_by_name = True


class CalculateSolarReturnDTO(BaseModel):
    """Data required to calculate solar return."""
    client_id: str = Field(..., alias='clientId')
    natal_chart_id: str = Field(..., alias='natalChartId')
    return_year: int = Field(..., alias='returnYear')
    location_city: str = Field(..., alias='locationCity')
    location_country: str = Field(..., alias='locationCountry')
    location_latitude: Optional[float] = Field(None, alias='locationLatitude')
    location_longitude: Optional[float] = Field(None, alias='locationLongitude')
    language: str = "en"

    class Config:
        populate_by_name = True


# ============================================================================
# Output DTOs
# ============================================================================

class NatalChartDTO(BaseModel):
    """Natal chart data returned to API consumers."""
    id: str
    client_id: str = Field(..., alias='clientId')
    name: str
    sun_sign: str = Field(..., alias='sunSign')
    planets: List[Dict]
    houses: List[Dict]
    aspects: List[Dict]
    angles: Dict
    solar_set: Dict = Field(..., alias='solarSet')
    interpretations: Dict[str, str]
    house_system: str = Field(..., alias='houseSystem')
    svg_url: Optional[str] = Field(None, alias='svgUrl')
    pdf_url: Optional[str] = Field(None, alias='pdfUrl')
    calculated_at: datetime = Field(..., alias='calculatedAt')
    created_at: datetime = Field(..., alias='createdAt')

    class Config:
        populate_by_name = True
        by_alias = True

    @classmethod
    def from_entity(cls, chart):
        """Create DTO from NatalChart entity."""
        return cls(
            id=str(chart.id),
            client_id=str(chart.client_id),
            name=chart.name,
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


class TransitDTO(BaseModel):
    """Transit data returned to API consumers."""
    id: str
    client_id: str = Field(..., alias='clientId')
    natal_chart_id: str = Field(..., alias='natalChartId')
    transit_date: datetime = Field(..., alias='transitDate')
    significant_aspects: List[Dict] = Field(..., alias='significantAspects')
    active_transits: List[Dict] = Field(..., alias='activeTransits')
    interpretations: Dict[str, str]
    calculated_at: datetime = Field(..., alias='calculatedAt')

    class Config:
        populate_by_name = True
        by_alias = True

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


class SolarReturnDTO(BaseModel):
    """Solar return data returned to API consumers."""
    id: str
    client_id: str = Field(..., alias='clientId')
    natal_chart_id: str = Field(..., alias='natalChartId')
    return_year: int = Field(..., alias='returnYear')
    return_datetime: datetime = Field(..., alias='returnDatetime')
    sun_sign: str = Field(..., alias='sunSign')
    planets: List[Dict]
    houses: List[Dict]
    aspects: List[Dict]
    solar_set: Dict = Field(..., alias='solarSet')
    interpretations: Dict[str, str]
    location_city: str = Field(..., alias='locationCity')
    location_country: str = Field(..., alias='locationCountry')
    is_relocated: bool = Field(..., alias='isRelocated')
    svg_url: Optional[str] = Field(None, alias='svgUrl')
    pdf_url: Optional[str] = Field(None, alias='pdfUrl')
    calculated_at: datetime = Field(..., alias='calculatedAt')

    class Config:
        populate_by_name = True
        by_alias = True

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
