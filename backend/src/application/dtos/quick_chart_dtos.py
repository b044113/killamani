"""
Quick Chart DTOs (Data Transfer Objects)

DTOs for quick chart calculation without requiring a client entity.
This allows any user to calculate a chart for MVP functionality.
"""
from dataclasses import dataclass
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

@dataclass
class QuickChartResultDTO:
    """
    Quick chart calculation result with SVG export.

    This DTO contains the calculated chart data and SVG visualization,
    without persisting to database (MVP requirement).
    """
    name: str
    sun_sign: str
    planets: List[Dict]
    houses: List[Dict]
    aspects: List[Dict]
    angles: Dict
    solar_set: Dict
    svg_data: str  # SVG content as string
    house_system: str
    calculated_at: datetime

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "sun_sign": self.sun_sign,
            "planets": self.planets,
            "houses": self.houses,
            "aspects": self.aspects,
            "angles": self.angles,
            "solar_set": self.solar_set,
            "svg_data": self.svg_data,
            "house_system": self.house_system,
            "calculated_at": self.calculated_at.isoformat(),
        }
