"""
Domain Entity: Transit

Represents transit calculations for a specific date.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4


@dataclass
class Transit:
    """
    Transit entity representing planetary transits for a specific date.

    Business Rules:
    - Must be associated with a client's natal chart
    - Transit date must be specified
    - Compares current planetary positions with natal positions
    - Identifies significant aspects and patterns
    """
    id: UUID = field(default_factory=uuid4)
    client_id: UUID = None  # Required
    natal_chart_id: UUID = None  # Required - reference to natal chart

    # Transit Information
    transit_date: datetime = None  # Date for which transits are calculated
    data: Dict = field(default_factory=dict)  # Transit positions and aspects

    # Significant Events
    significant_aspects: List[Dict] = field(default_factory=list)  # Important transits
    active_transits: List[Dict] = field(default_factory=list)  # Currently active transits

    # Metadata
    calculated_at: datetime = field(default_factory=datetime.utcnow)

    # Interpretations (multilingual)
    interpretations: Dict[str, Dict] = field(default_factory=dict)  # {language: {aspect: text}}

    # Audit
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate entity after initialization"""
        if not self.client_id:
            raise ValueError("Transit must be associated with a client")
        if not self.natal_chart_id:
            raise ValueError("Transit must be associated with a natal chart")
        if not self.transit_date:
            raise ValueError("Transit date is required")

    def add_significant_aspect(self, aspect: Dict):
        """Add a significant transit aspect"""
        required_fields = ["transiting_planet", "natal_planet", "aspect_type", "orb"]
        if not all(field in aspect for field in required_fields):
            raise ValueError(f"Aspect must contain fields: {required_fields}")
        self.significant_aspects.append(aspect)
        self.updated_at = datetime.utcnow()

    def add_active_transit(self, transit: Dict):
        """Add an active transit"""
        required_fields = ["planet", "sign", "house", "start_date", "end_date"]
        if not all(field in transit for field in required_fields):
            raise ValueError(f"Transit must contain fields: {required_fields}")
        self.active_transits.append(transit)
        self.updated_at = datetime.utcnow()

    def has_interpretation(self, language: str) -> bool:
        """Check if transit has interpretation in given language"""
        return language in self.interpretations

    def add_interpretation(self, language: str, interpretation: Dict):
        """Add interpretation for a specific language"""
        supported_languages = ["es", "en", "it", "fr", "de", "pt-br"]
        if language not in supported_languages:
            raise ValueError(f"Unsupported language: {language}")
        self.interpretations[language] = interpretation
        self.updated_at = datetime.utcnow()

    def get_transiting_planets(self) -> List[Dict]:
        """Extract transiting planet positions"""
        return self.data.get("transiting_planets", [])

    def get_natal_aspects(self) -> List[Dict]:
        """Extract natal-transit aspects"""
        return self.data.get("natal_aspects", [])

    @property
    def has_significant_aspects(self) -> bool:
        """Check if transit has any significant aspects"""
        return len(self.significant_aspects) > 0

    @property
    def aspect_count(self) -> int:
        """Get count of significant aspects"""
        return len(self.significant_aspects)

    def is_for_date(self, date: datetime) -> bool:
        """Check if transit is calculated for a specific date"""
        return self.transit_date.date() == date.date()
