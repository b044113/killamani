"""
Authentication DTOs (Data Transfer Objects)

Input/Output data structures for authentication use cases.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from ...domain.entities.user import UserRole


# ============================================================================
# Input DTOs
# ============================================================================

class LoginDTO(BaseModel):
    """Data required for user login."""
    email: str
    password: str


class RegisterUserDTO(BaseModel):
    """Data required for user registration."""
    email: str
    password: str
    role: UserRole = UserRole.USER
    preferred_language: str = "en"


class RefreshTokenDTO(BaseModel):
    """Data required for token refresh."""
    refresh_token: str


class ResetPasswordDTO(BaseModel):
    """Data required for password reset."""
    email: str
    new_password: str
    reset_token: str


# ============================================================================
# Output DTOs
# ============================================================================

class AuthTokensDTO(BaseModel):
    """Authentication tokens returned after successful login."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes


class UserDTO(BaseModel):
    """User data returned to clients."""
    id: str
    email: str
    role: str
    is_active: bool
    preferred_language: str
    created_at: datetime
    consultant_id: Optional[str] = None

    @classmethod
    def from_entity(cls, user):
        """Create DTO from User entity."""
        return cls(
            id=str(user.id),
            email=user.email,
            role=user.role.value,
            is_active=user.is_active,
            preferred_language=user.preferred_language,
            created_at=user.created_at,
            consultant_id=str(user.consultant_id) if user.consultant_id else None,
        )
