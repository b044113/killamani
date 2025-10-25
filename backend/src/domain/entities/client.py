"""
Domain Entity: Client

Represents a client managed by a consultant.
Contains birth data and relationship to their consultant.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from ..value_objects.birth_data import BirthData


@dataclass
class Client:
    """
    Client entity representing a person whose chart is calculated.

    Business Rules:
    - Must have birth data (date, time, location)
    - Must be associated with a consultant
    - Can have user account (optional)
    - Birth data is immutable once set
    """
    id: UUID = field(default_factory=uuid4)
    consultant_id: UUID = None  # Required
    user_id: Optional[UUID] = None  # Optional - if client has login access

    # Personal Information
    first_name: str = ""
    last_name: str = ""
    email: Optional[str] = None
    phone: Optional[str] = None

    # Birth Data (Value Object) - Optional now, as charts are separate
    birth_data: Optional[BirthData] = None

    # Metadata
    notes: str = ""  # Consultant's private notes
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate entity after initialization"""
        if not self.consultant_id:
            raise ValueError("Client must be associated with a consultant")
        if not self.first_name:
            raise ValueError("First name is required")
        # Note: birth_data is now optional - clients can exist without charts

    @property
    def full_name(self) -> str:
        """Get client's full name"""
        return f"{self.first_name} {self.last_name}".strip()

    def has_account(self) -> bool:
        """Check if client has user account for login"""
        return self.user_id is not None

    def belongs_to_consultant(self, consultant_id: UUID) -> bool:
        """Check if client belongs to a specific consultant"""
        return self.consultant_id == consultant_id

    def update_notes(self, notes: str):
        """Update consultant's notes about this client"""
        self.notes = notes
        self.updated_at = datetime.utcnow()

    def update_contact_info(self, email: Optional[str] = None, phone: Optional[str] = None):
        """Update client's contact information"""
        if email is not None:
            self.email = email
        if phone is not None:
            self.phone = phone
        self.updated_at = datetime.utcnow()
