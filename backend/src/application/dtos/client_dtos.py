"""
Client DTOs (Data Transfer Objects)

Input/Output data structures for client management use cases.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


# ============================================================================
# Input DTOs
# ============================================================================

@dataclass
class BirthDataDTO:
    """Birth data for client."""
    date: datetime
    city: str
    country: str
    timezone: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@dataclass
class CreateClientDTO:
    """Data required to create a new client."""
    first_name: str
    last_name: str
    birth_data: BirthDataDTO
    email: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class UpdateClientDTO:
    """Data for updating an existing client."""
    client_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class SearchClientsDTO:
    """Data for searching clients."""
    query: str
    skip: int = 0
    limit: int = 100


# ============================================================================
# Output DTOs
# ============================================================================

@dataclass
class ClientDTO:
    """Client data returned to API consumers."""
    id: str
    consultant_id: str
    first_name: str
    last_name: str
    full_name: str
    email: Optional[str]
    birth_date: str
    birth_city: str
    birth_country: str
    birth_timezone: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    has_account: bool = False

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
            birth_date=client.birth_data.date.isoformat(),
            birth_city=client.birth_data.city,
            birth_country=client.birth_data.country,
            birth_timezone=client.birth_data.timezone,
            notes=client.notes,
            created_at=client.created_at,
            updated_at=client.updated_at,
            has_account=client.has_account(),
        )


@dataclass
class ClientListDTO:
    """List of clients with pagination info."""
    clients: list[ClientDTO]
    total: int
    skip: int
    limit: int
