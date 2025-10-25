"""
Authentication DTOs (Data Transfer Objects)

Input/Output data structures for authentication use cases.
All DTOs use Pydantic with camelCase aliases for frontend compatibility.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

from ...domain.entities.user import UserRole


# ============================================================================
# Input DTOs (Pydantic with validation)
# ============================================================================

class LoginDTO(BaseModel):
    """Data required for user login."""
    email: EmailStr
    password: str = Field(..., min_length=6)

    class Config:
        populate_by_name = True


class RegisterUserDTO(BaseModel):
    """Data required for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.USER
    preferred_language: str = Field("en", alias='preferredLanguage')

    class Config:
        populate_by_name = True


class RefreshTokenDTO(BaseModel):
    """Data required for token refresh."""
    refresh_token: str = Field(..., alias='refreshToken')

    class Config:
        populate_by_name = True


class ResetPasswordDTO(BaseModel):
    """Data required for password reset."""
    email: EmailStr
    new_password: str = Field(..., min_length=6, alias='newPassword')
    reset_token: str = Field(..., alias='resetToken')

    class Config:
        populate_by_name = True


# ============================================================================
# Output DTOs (Pydantic with camelCase aliases)
# ============================================================================

class AuthTokensDTO(BaseModel):
    """Authentication tokens returned after successful login."""
    access_token: str = Field(..., alias='accessToken')
    refresh_token: str = Field(..., alias='refreshToken')
    token_type: str = Field("bearer", alias='tokenType')
    expires_in: int = Field(1800, alias='expiresIn')  # 30 minutes

    class Config:
        populate_by_name = True
        by_alias = True  # Always use aliases when serializing


class UserDTO(BaseModel):
    """User data returned to clients."""
    id: str
    email: str
    role: str
    is_active: bool = Field(..., alias='isActive')
    preferred_language: str = Field(..., alias='preferredLanguage')
    created_at: datetime = Field(..., alias='createdAt')
    consultant_id: Optional[str] = Field(None, alias='consultantId')

    class Config:
        populate_by_name = True
        by_alias = True  # Always use aliases when serializing

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
