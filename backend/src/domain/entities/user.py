"""
Domain Entity: User

This is a framework-agnostic domain entity representing a user in the system.
Contains business logic and invariants.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class UserRole(str, Enum):
    """User roles with hierarchical permissions"""
    ADMIN = "admin"
    CONSULTANT = "consultant"
    CLIENT = "client"
    USER = "user"


@dataclass
class User:
    """
    User entity with role-based access control.

    Business Rules:
    - Email must be unique
    - Admin can manage consultants
    - Consultant can manage clients
    - Client can only view own data
    - User can calculate one chart
    """
    id: UUID = field(default_factory=uuid4)
    email: str = ""
    hashed_password: str = ""
    role: UserRole = UserRole.USER
    is_active: bool = True
    is_first_login: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Relationships
    consultant_id: Optional[UUID] = None  # For clients, who is their consultant
    preferred_language: str = "en"

    def __post_init__(self):
        """Validate entity after initialization"""
        if not self.email:
            raise ValueError("Email is required")
        if "@" not in self.email:
            raise ValueError("Invalid email format")

    def can_manage_consultants(self) -> bool:
        """Check if user can create/manage consultants"""
        return self.role == UserRole.ADMIN

    def can_manage_clients(self) -> bool:
        """Check if user can create/manage clients"""
        return self.role in [UserRole.ADMIN, UserRole.CONSULTANT]

    def can_view_client(self, client_id: UUID) -> bool:
        """Check if user can view a specific client"""
        if self.role == UserRole.ADMIN:
            return True
        if self.role == UserRole.CONSULTANT:
            # Consultant can view their own clients
            return True  # Will be validated at repository level
        if self.role == UserRole.CLIENT:
            # Client can only view themselves
            return self.id == client_id
        return False

    def can_calculate_charts(self) -> bool:
        """Check if user can calculate astrological charts"""
        return self.role in [UserRole.ADMIN, UserRole.CONSULTANT, UserRole.USER]

    def requires_password_reset(self) -> bool:
        """Check if user needs to set password on first login"""
        return self.is_first_login and self.role == UserRole.CLIENT

    def activate(self):
        """Activate user account"""
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def deactivate(self):
        """Deactivate user account"""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def complete_first_login(self):
        """Mark first login as complete"""
        self.is_first_login = False
        self.updated_at = datetime.utcnow()

    def change_language(self, language: str):
        """Change user's preferred language"""
        supported_languages = ["es", "en", "it", "fr", "de", "pt-br"]
        if language not in supported_languages:
            raise ValueError(f"Unsupported language: {language}")
        self.preferred_language = language
        self.updated_at = datetime.utcnow()
