"""
Application DTOs (Data Transfer Objects)

Input/Output data structures for use cases.
"""
from .auth_dtos import (
    LoginDTO,
    RegisterUserDTO,
    RefreshTokenDTO,
    AuthTokensDTO,
    UserDTO,
)
from .client_dtos import (
    BirthDataDTO,
    CreateClientDTO,
    UpdateClientDTO,
    SearchClientsDTO,
    ClientDTO,
    ClientListDTO,
)
from .chart_dtos import (
    CalculateNatalChartDTO,
    CalculateTransitsDTO,
    CalculateSolarReturnDTO,
    NatalChartDTO,
    TransitDTO,
    SolarReturnDTO,
)

__all__ = [
    # Auth DTOs
    "LoginDTO",
    "RegisterUserDTO",
    "RefreshTokenDTO",
    "AuthTokensDTO",
    "UserDTO",
    # Client DTOs
    "BirthDataDTO",
    "CreateClientDTO",
    "UpdateClientDTO",
    "SearchClientsDTO",
    "ClientDTO",
    "ClientListDTO",
    # Chart DTOs
    "CalculateNatalChartDTO",
    "CalculateTransitsDTO",
    "CalculateSolarReturnDTO",
    "NatalChartDTO",
    "TransitDTO",
    "SolarReturnDTO",
]
