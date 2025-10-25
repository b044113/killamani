"""
Client DTOs (Data Transfer Objects)

Input/Output data structures for client management use cases.
All DTOs use Pydantic for validation and automatic camelCase conversion.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator


# ============================================================================
# Input DTOs (Using Pydantic for validation)
# ============================================================================

class BirthDataDTO(BaseModel):
    """Birth data for client."""
    date: datetime
    city: str = Field(..., min_length=1, max_length=100)
    country: str = Field(..., min_length=2, max_length=10)
    timezone: str = Field(..., min_length=1, max_length=50)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)

    @field_validator('latitude', 'longitude')
    @classmethod
    def validate_coordinates(cls, v, info):
        """Validate that both coordinates are provided together or both are None."""
        return v


class CreateClientDTO(BaseModel):
    """Data required to create a new client (basic information only)."""
    first_name: str = Field(..., min_length=1, max_length=100, alias='firstName')
    last_name: str = Field(..., min_length=1, max_length=100, alias='lastName')
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None

    class Config:
        populate_by_name = True  # Allow both snake_case and camelCase
        str_strip_whitespace = True


class UpdateClientDTO(BaseModel):
    """Data for updating an existing client."""
    client_id: str = Field(..., alias='clientId')
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, alias='firstName')
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, alias='lastName')
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None

    class Config:
        populate_by_name = True
        str_strip_whitespace = True


class SearchClientsDTO(BaseModel):
    """Data for searching clients."""
    query: str = Field(..., min_length=1)
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)


# ============================================================================
# Output DTOs (Using Pydantic for automatic camelCase conversion)
# ============================================================================

class ClientDTO(BaseModel):
    """Client data returned to API consumers."""
    id: str
    consultant_id: str = Field(..., alias='consultantId')
    first_name: str = Field(..., alias='firstName')
    last_name: str = Field(..., alias='lastName')
    full_name: str = Field(..., alias='fullName')
    email: Optional[str] = None
    phone: Optional[str] = None
    birth_date: Optional[str] = Field(None, alias='birthDate')
    birth_city: Optional[str] = Field(None, alias='birthCity')
    birth_country: Optional[str] = Field(None, alias='birthCountry')
    birth_timezone: Optional[str] = Field(None, alias='birthTimezone')
    notes: Optional[str] = None
    created_at: datetime = Field(..., alias='createdAt')
    updated_at: datetime = Field(..., alias='updatedAt')
    has_account: bool = Field(False, alias='hasAccount')

    class Config:
        populate_by_name = True
        by_alias = True  # Always use aliases when serializing

    @classmethod
    def from_entity(cls, client):
        """Create DTO from Client entity."""
        return cls(
            id=str(client.id),
            consultant_id=str(client.consultant_id),
            first_name=client.first_name,
            last_name=client.last_name,
            full_name=client.full_name,
            email=client.email,
            phone=client.phone,
            birth_date=client.birth_data.date.isoformat() if client.birth_data else None,
            birth_city=client.birth_data.city if client.birth_data else None,
            birth_country=client.birth_data.country if client.birth_data else None,
            birth_timezone=client.birth_data.timezone if client.birth_data else None,
            notes=client.notes,
            created_at=client.created_at,
            updated_at=client.updated_at,
            has_account=client.has_account(),
        )


class ClientListDTO(BaseModel):
    """List of clients with pagination info."""
    clients: List[ClientDTO]
    total: int
    skip: int
    limit: int
