"""
Domain Entity: SolarReturn

Represents a solar return chart for a specific year.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4


@dataclass
class SolarReturn:
    """
    Solar Return entity representing an annual chart when the Sun returns to its natal position.

    Business Rules:
    - Must be associated with a client's natal chart
    - Return year must be specified
    - Calculated for exact moment Sun returns to natal position
    - Location can be current residence (relocation chart) or birth location
    """
    id: UUID = field(default_factory=uuid4)
    client_id: UUID = None  # Required
    natal_chart_id: UUID = None  # Required - reference to natal chart

    # Solar Return Information
    return_year: int = None  # Year for which solar return is calculated
    return_datetime: datetime = None  # Exact moment of solar return
    location_city: str = ""  # Location where chart is calculated
    location_country: str = ""
    location_latitude: Optional[float] = None
    location_longitude: Optional[float] = None

    # Chart Data
    data: Dict = field(default_factory=dict)  # Calculated chart data
    solar_set: Dict = field(default_factory=dict)  # Solar return solar set

    # Metadata
    house_system: str = "placidus"
    is_relocated: bool = False  # True if calculated for different location than birth
    calculated_at: datetime = field(default_factory=datetime.utcnow)

    # Interpretations (multilingual)
    interpretations: Dict[str, Dict] = field(default_factory=dict)  # {language: {aspect: text}}

    # Export paths
    svg_url: Optional[str] = None
    pdf_url: Optional[str] = None

    # Audit
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate entity after initialization"""
        if not self.client_id:
            raise ValueError("Solar return must be associated with a client")
        if not self.natal_chart_id:
            raise ValueError("Solar return must be associated with a natal chart")
        if not self.return_year:
            raise ValueError("Return year is required")
        if not self.return_datetime:
            raise ValueError("Return datetime is required")
        if not self.location_city:
            raise ValueError("Location city is required")
        if not self.location_country:
            raise ValueError("Location country is required")

    def has_interpretation(self, language: str) -> bool:
        """Check if solar return has interpretation in given language"""
        return language in self.interpretations

    def add_interpretation(self, language: str, interpretation: Dict):
        """Add interpretation for a specific language"""
        supported_languages = ["es", "en", "it", "fr", "de", "pt-br"]
        if language not in supported_languages:
            raise ValueError(f"Unsupported language: {language}")
        self.interpretations[language] = interpretation
        self.updated_at = datetime.utcnow()

    def set_svg_export(self, url: str):
        """Set SVG export URL"""
        self.svg_url = url
        self.updated_at = datetime.utcnow()

    def set_pdf_export(self, url: str):
        """Set PDF export URL"""
        self.pdf_url = url
        self.updated_at = datetime.utcnow()

    def mark_as_relocated(self):
        """Mark chart as relocated (calculated for different location)"""
        self.is_relocated = True
        self.updated_at = datetime.utcnow()

    def get_planets(self) -> List[Dict]:
        """Extract planet positions from chart data"""
        return self.data.get("planets", [])

    def get_houses(self) -> List[Dict]:
        """Extract house positions from chart data"""
        return self.data.get("houses", [])

    def get_aspects(self) -> List[Dict]:
        """Extract aspects from chart data"""
        return self.data.get("aspects", [])

    def get_angles(self) -> Dict:
        """Extract angles (Ascendant, MC, etc.) from chart data"""
        return self.data.get("angles", {})

    @property
    def sun_sign(self) -> str:
        """Get sun sign from solar set"""
        return self.solar_set.get("sun_sign", "Unknown")

    @property
    def has_exports(self) -> bool:
        """Check if solar return has any exports"""
        return self.svg_url is not None or self.pdf_url is not None

    @property
    def age_at_return(self) -> int:
        """Calculate age at solar return"""
        return self.return_year - self.return_datetime.year

    def is_for_year(self, year: int) -> bool:
        """Check if solar return is for a specific year"""
        return self.return_year == year
