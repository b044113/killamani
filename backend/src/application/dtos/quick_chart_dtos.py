"""
Quick Chart DTOs (Data Transfer Objects)

DTOs for quick chart calculation without requiring a client entity.
This allows any user to calculate a chart for MVP functionality.
All DTOs use Pydantic with camelCase aliases for frontend compatibility.
"""
from typing import Optional, Dict, List
from datetime import datetime
from pydantic import BaseModel, Field


# ============================================================================
# Input DTOs
# ============================================================================

class QuickCalculateChartDTO(BaseModel):
    """
    Data required to calculate a quick natal chart without client creation.

    This DTO supports the MVP requirement where any user (admin, consultant,
    or anonymous user) can calculate a chart by providing birth data directly.
    """
    name: str
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
                "name": "John Doe",
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


# ============================================================================
# Output DTOs
# ============================================================================

class QuickChartResultDTO(BaseModel):
    """
    Quick chart calculation result with SVG export.

    This DTO contains the calculated chart data and SVG visualization,
    without persisting to database (MVP requirement).
    """
    name: str
    sun_sign: str = Field(..., alias='sunSign')
    planets: List[Dict]
    houses: List[Dict]
    aspects: List[Dict]
    angles: Dict
    solar_set: Dict = Field(..., alias='solarSet')
    svg_data: str = Field(..., alias='svgData')  # SVG content as string
    house_system: str = Field(..., alias='houseSystem')
    calculated_at: datetime = Field(..., alias='calculatedAt')

    class Config:
        populate_by_name = True
        by_alias = True
