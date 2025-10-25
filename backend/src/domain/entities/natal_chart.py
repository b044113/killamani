"""
Domain Entity: NatalChart

Represents a calculated natal (birth) chart with all astrological data.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4


@dataclass
class NatalChart:
    """
    Natal Chart entity representing a calculated astrological birth chart.

    Business Rules:
    - Must be associated with a client
    - Chart data is immutable once calculated
    - Contains planets, houses, aspects, and interpretations
    - Can be exported to various formats (SVG, PDF)
    """
    id: UUID = field(default_factory=uuid4)
    client_id: UUID = None  # Required

    # Chart Information
    name: str = "Birth Chart"  # Descriptive name for this chart

    # Chart Calculation Data
    data: Dict = field(default_factory=dict)  # Raw calculation data (planets, houses, etc.)
    solar_set: Dict = field(default_factory=dict)  # Sun sign, 5th house, hard aspects

    # Metadata
    house_system: str = "placidus"  # placidus, koch, equal, whole_sign
    calculated_at: datetime = field(default_factory=datetime.utcnow)

    # Interpretations (multilingual)
    interpretations: Dict[str, Dict] = field(default_factory=dict)  # {language: {planet: text}}

    # Export paths
    svg_url: Optional[str] = None
    pdf_url: Optional[str] = None

    # Audit
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate entity after initialization"""
        if not self.client_id:
            raise ValueError("Chart must be associated with a client")
        if not self.data:
            raise ValueError("Chart data is required")

    def has_interpretation(self, language: str) -> bool:
        """Check if chart has interpretation in given language"""
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
        """Check if chart has any exports"""
        return self.svg_url is not None or self.pdf_url is not None
