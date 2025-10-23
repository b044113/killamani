"""
FastAPI Dependencies

Dependency injection for repositories, services, and use cases.
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ....domain.entities.user import User
from ....domain.exceptions import InvalidCredentialsError, UserNotFoundError
from ....infrastructure.database.connection import get_db
from ....application.services.token_service import TokenService
from ....application.services.password_service import PasswordService

# Repositories
from ....adapters.repositories.sqlalchemy import (
    SQLAlchemyUserRepository,
    SQLAlchemyClientRepository,
    SQLAlchemyNatalChartRepository,
    SQLAlchemyTransitRepository,
    SQLAlchemySolarReturnRepository,
    SQLAlchemyAuditRepository,
)

# Adapters
from ....adapters.calculators import KerykeionCalculator
from ....adapters.storage import LocalFileStorage
from ....adapters.interpreters import RuleBasedInterpreter

# Use Cases
from ....application.use_cases.auth import (
    LoginUseCase,
    RegisterUserUseCase,
    RefreshTokenUseCase,
)
from ....application.use_cases.client_management import (
    CreateClientUseCase,
    ListClientsUseCase,
    GetClientDetailsUseCase,
    UpdateClientUseCase,
    SearchClientsUseCase,
)
from ....application.use_cases.chart_calculation import (
    CalculateNatalChartUseCase,
    GetChartDetailsUseCase,
    ListClientChartsUseCase,
)


# ============================================================================
# Security
# ============================================================================

security = HTTPBearer()


# ============================================================================
# Services
# ============================================================================

def get_password_service() -> PasswordService:
    """Get password service instance."""
    return PasswordService()


def get_token_service() -> TokenService:
    """Get token service instance."""
    return TokenService()


# ============================================================================
# Repositories
# ============================================================================

def get_user_repository(db: Session = Depends(get_db)) -> SQLAlchemyUserRepository:
    """Get user repository instance."""
    return SQLAlchemyUserRepository(db)


def get_client_repository(db: Session = Depends(get_db)) -> SQLAlchemyClientRepository:
    """Get client repository instance."""
    return SQLAlchemyClientRepository(db)


def get_natal_chart_repository(db: Session = Depends(get_db)) -> SQLAlchemyNatalChartRepository:
    """Get natal chart repository instance."""
    return SQLAlchemyNatalChartRepository(db)


def get_transit_repository(db: Session = Depends(get_db)) -> SQLAlchemyTransitRepository:
    """Get transit repository instance."""
    return SQLAlchemyTransitRepository(db)


def get_solar_return_repository(db: Session = Depends(get_db)) -> SQLAlchemySolarReturnRepository:
    """Get solar return repository instance."""
    return SQLAlchemySolarReturnRepository(db)


def get_audit_repository(db: Session = Depends(get_db)) -> SQLAlchemyAuditRepository:
    """Get audit repository instance."""
    return SQLAlchemyAuditRepository(db)


# ============================================================================
# Adapters
# ============================================================================

def get_astro_calculator() -> Optional[KerykeionCalculator]:
    """Get astrological calculator instance."""
    try:
        return KerykeionCalculator()
    except ImportError as e:
        # Kerykeion not installed - return None for now
        # Chart calculation endpoints will return a 501 Not Implemented
        return None


def get_file_storage() -> LocalFileStorage:
    """Get file storage instance."""
    return LocalFileStorage()


def get_chart_interpreter() -> RuleBasedInterpreter:
    """Get chart interpreter instance."""
    return RuleBasedInterpreter()


# ============================================================================
# Authentication
# ============================================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    token_service: TokenService = Depends(get_token_service),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository)
) -> User:
    """
    Get current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer token
        token_service: Token service for JWT verification
        user_repo: User repository

    Returns:
        Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        # Verify token and get user ID
        user_id = token_service.verify_token(credentials.credentials, token_type="access")

        # Get user from database
        user = user_repo.find_by_id(user_id)

        if not user:
            raise UserNotFoundError(str(user_id))

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        return user

    except (InvalidCredentialsError, UserNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ============================================================================
# Use Cases - Auth
# ============================================================================

def get_login_use_case(
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
    password_service: PasswordService = Depends(get_password_service),
    token_service: TokenService = Depends(get_token_service)
) -> LoginUseCase:
    """Get login use case instance."""
    return LoginUseCase(user_repo, password_service, token_service)


def get_register_user_use_case(
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
    password_service: PasswordService = Depends(get_password_service)
) -> RegisterUserUseCase:
    """Get register user use case instance."""
    return RegisterUserUseCase(user_repo, password_service)


def get_refresh_token_use_case(
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
    token_service: TokenService = Depends(get_token_service)
) -> RefreshTokenUseCase:
    """Get refresh token use case instance."""
    return RefreshTokenUseCase(user_repo, token_service)


# ============================================================================
# Use Cases - Client Management
# ============================================================================

def get_create_client_use_case(
    client_repo: SQLAlchemyClientRepository = Depends(get_client_repository),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository)
) -> CreateClientUseCase:
    """Get create client use case instance."""
    return CreateClientUseCase(client_repo, user_repo)


def get_list_clients_use_case(
    client_repo: SQLAlchemyClientRepository = Depends(get_client_repository)
) -> ListClientsUseCase:
    """Get list clients use case instance."""
    return ListClientsUseCase(client_repo)


def get_client_details_use_case(
    client_repo: SQLAlchemyClientRepository = Depends(get_client_repository)
) -> GetClientDetailsUseCase:
    """Get client details use case instance."""
    return GetClientDetailsUseCase(client_repo)


def get_update_client_use_case(
    client_repo: SQLAlchemyClientRepository = Depends(get_client_repository)
) -> UpdateClientUseCase:
    """Get update client use case instance."""
    return UpdateClientUseCase(client_repo)


def get_search_clients_use_case(
    client_repo: SQLAlchemyClientRepository = Depends(get_client_repository)
) -> SearchClientsUseCase:
    """Get search clients use case instance."""
    return SearchClientsUseCase(client_repo)


# ============================================================================
# Use Cases - Chart Calculation
# ============================================================================

def get_calculate_natal_chart_use_case(
    client_repo: SQLAlchemyClientRepository = Depends(get_client_repository),
    chart_repo: SQLAlchemyNatalChartRepository = Depends(get_natal_chart_repository),
    calculator: KerykeionCalculator = Depends(get_astro_calculator),
    interpreter: RuleBasedInterpreter = Depends(get_chart_interpreter)
) -> CalculateNatalChartUseCase:
    """Get calculate natal chart use case instance."""
    return CalculateNatalChartUseCase(client_repo, chart_repo, calculator, interpreter)


def get_chart_details_use_case(
    client_repo: SQLAlchemyClientRepository = Depends(get_client_repository),
    chart_repo: SQLAlchemyNatalChartRepository = Depends(get_natal_chart_repository)
) -> GetChartDetailsUseCase:
    """Get chart details use case instance."""
    return GetChartDetailsUseCase(client_repo, chart_repo)


def get_list_client_charts_use_case(
    client_repo: SQLAlchemyClientRepository = Depends(get_client_repository),
    chart_repo: SQLAlchemyNatalChartRepository = Depends(get_natal_chart_repository)
) -> ListClientChartsUseCase:
    """Get list client charts use case instance."""
    return ListClientChartsUseCase(client_repo, chart_repo)
