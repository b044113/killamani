"""
Test configuration and shared fixtures
"""
import asyncio
import os
from typing import AsyncGenerator, Generator
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.main import app
from src.infrastructure.database.models import Base
from src.infrastructure.api.dependencies.dependencies import get_db
from src.domain.entities.user import User, UserRole
from src.domain.value_objects.birth_data import BirthData
from src.application.services.password_service import PasswordService
from src.application.services.token_service import TokenService


# Test database configuration - PostgreSQL test database
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://astrojoy:astrojoy2024@localhost:5432/astrojoy_test"
)

# Create test engine
test_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a fresh database session for each test"""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)

    # Create session
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> TestClient:
    """Create test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def password_service() -> PasswordService:
    """Password service instance"""
    return PasswordService()


@pytest.fixture
def token_service(monkeypatch) -> TokenService:
    """Token service instance with test configuration"""
    # Mock settings for testing
    from src.infrastructure.config.settings import Settings

    test_settings = Settings(
        JWT_SECRET_KEY="test-secret-key-for-testing-only",
        JWT_ALGORITHM="HS256",
        JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30,
        JWT_REFRESH_TOKEN_EXPIRE_DAYS=7,
        DATABASE_URL="sqlite:///:memory:"
    )

    monkeypatch.setattr("src.application.services.token_service.settings", test_settings)
    return TokenService()


# ============================================================================
# User Fixtures
# ============================================================================

@pytest.fixture
def admin_user(password_service: PasswordService) -> User:
    """Create admin user entity"""
    from uuid import UUID
    return User(
        id=UUID("12345678-1234-1234-1234-123456789001"),
        email="admin@test.com",
        hashed_password=password_service.hash_password("admin123"),
        role=UserRole.ADMIN,
        is_active=True,
        preferred_language="en",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


@pytest.fixture
def consultant_user(password_service: PasswordService) -> User:
    """Create consultant user entity"""
    from uuid import UUID
    return User(
        id=UUID("12345678-1234-1234-1234-123456789002"),
        email="consultant@test.com",
        hashed_password=password_service.hash_password("consultant123"),
        role=UserRole.CONSULTANT,
        is_active=True,
        preferred_language="en",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


@pytest.fixture
def regular_user(password_service: PasswordService) -> User:
    """Create regular user entity"""
    from uuid import UUID
    return User(
        id=UUID("12345678-1234-1234-1234-123456789003"),
        email="user@test.com",
        hashed_password=password_service.hash_password("user123"),
        role=UserRole.USER,
        is_active=True,
        preferred_language="en",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


@pytest.fixture
def inactive_user(password_service: PasswordService) -> User:
    """Create inactive user entity"""
    from uuid import UUID
    return User(
        id=UUID("12345678-1234-1234-1234-123456789004"),
        email="inactive@test.com",
        hashed_password=password_service.hash_password("inactive123"),
        role=UserRole.USER,
        is_active=False,
        preferred_language="en",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


# ============================================================================
# Token Fixtures
# ============================================================================

@pytest.fixture
def admin_token(token_service: TokenService, admin_user: User) -> str:
    """Generate access token for admin user"""
    return token_service.create_access_token(
        admin_user.id,
        additional_claims={"role": admin_user.role.value}
    )


@pytest.fixture
def consultant_token(token_service: TokenService, consultant_user: User) -> str:
    """Generate access token for consultant user"""
    return token_service.create_access_token(
        consultant_user.id,
        additional_claims={"role": consultant_user.role.value}
    )


@pytest.fixture
def user_token(token_service: TokenService, regular_user: User) -> str:
    """Generate access token for regular user"""
    return token_service.create_access_token(
        regular_user.id,
        additional_claims={"role": regular_user.role.value}
    )


# ============================================================================
# Birth Data Fixtures
# ============================================================================

@pytest.fixture
def sample_birth_data() -> BirthData:
    """Sample birth data for testing"""
    return BirthData(
        date=datetime(1990, 5, 15, 14, 30, tzinfo=timezone.utc),
        city="New York",
        country="US",
        timezone="America/New_York",
        latitude=40.7128,
        longitude=-74.0060
    )


@pytest.fixture
def alternative_birth_data() -> BirthData:
    """Alternative birth data for testing"""
    return BirthData(
        date=datetime(1985, 10, 20, 8, 45, tzinfo=timezone.utc),
        city="London",
        country="GB",
        timezone="Europe/London",
        latitude=51.5074,
        longitude=-0.1278
    )


# ============================================================================
# Database Model Fixtures
# ============================================================================

@pytest.fixture
def create_db_user(db_session: Session):
    """Factory to create user in database"""
    from src.infrastructure.database.models import UserModel
    from uuid import UUID, uuid4

    def _create_user(**kwargs):
        # Convert string ID to UUID if needed
        user_id = kwargs.get("id")
        if user_id is None:
            user_id = uuid4()
        elif isinstance(user_id, str):
            try:
                user_id = UUID(user_id)
            except ValueError:
                user_id = uuid4()
        elif not isinstance(user_id, UUID):
            user_id = uuid4()

        # Handle consultant_id if provided
        consultant_id = kwargs.get("consultant_id")
        if consultant_id is not None:
            if isinstance(consultant_id, str):
                try:
                    consultant_id = UUID(consultant_id)
                except ValueError:
                    consultant_id = None
            elif not isinstance(consultant_id, UUID):
                consultant_id = None

        user_data = {
            "id": user_id,
            "email": kwargs.get("email", "test@example.com"),
            "hashed_password": kwargs.get("hashed_password", "hashed_password"),
            "role": kwargs.get("role", "user"),
            "is_active": kwargs.get("is_active", True),
            "is_first_login": kwargs.get("is_first_login", True),
            "preferred_language": kwargs.get("preferred_language", "en"),
            "consultant_id": consultant_id,
            "created_at": kwargs.get("created_at", datetime.now(timezone.utc)),
            "updated_at": kwargs.get("updated_at", datetime.now(timezone.utc))
        }
        user = UserModel(**user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _create_user


@pytest.fixture
def create_db_client(db_session: Session):
    """Factory to create client in database"""
    from src.infrastructure.database.models import ClientModel
    from uuid import UUID, uuid4

    def _create_client(**kwargs):
        # Convert string IDs to UUID if needed
        client_id = kwargs.get("id")
        if client_id is None:
            client_id = uuid4()
        elif isinstance(client_id, str):
            try:
                client_id = UUID(client_id)
            except ValueError:
                client_id = uuid4()
        elif not isinstance(client_id, UUID):
            client_id = uuid4()

        consultant_id = kwargs.get("consultant_id")
        if consultant_id is None:
            consultant_id = uuid4()
        elif isinstance(consultant_id, str):
            try:
                consultant_id = UUID(consultant_id)
            except ValueError:
                consultant_id = uuid4()
        elif not isinstance(consultant_id, UUID):
            consultant_id = uuid4()

        client_data = {
            "id": client_id,
            "consultant_id": consultant_id,
            "first_name": kwargs.get("first_name", "John"),
            "last_name": kwargs.get("last_name", "Doe"),
            "email": kwargs.get("email", "john.doe@example.com"),
            "birth_date": kwargs.get("birth_date", datetime(1990, 5, 15, 14, 30, tzinfo=timezone.utc)),
            "birth_city": kwargs.get("birth_city", "New York"),
            "birth_country": kwargs.get("birth_country", "US"),
            "birth_timezone": kwargs.get("birth_timezone", "America/New_York"),
            "birth_latitude": kwargs.get("birth_latitude", 40.7128),
            "birth_longitude": kwargs.get("birth_longitude", -74.0060),
            "notes": kwargs.get("notes"),
            "created_at": kwargs.get("created_at", datetime.now(timezone.utc)),
            "updated_at": kwargs.get("updated_at", datetime.now(timezone.utc))
        }
        client = ClientModel(**client_data)
        db_session.add(client)
        db_session.commit()
        db_session.refresh(client)
        return client

    return _create_client


@pytest.fixture
def create_db_chart(db_session: Session):
    """Factory to create natal chart in database"""
    from src.infrastructure.database.models import NatalChartModel
    from uuid import UUID, uuid4

    def _create_chart(**kwargs):
        # Convert string IDs to UUID if needed
        chart_id = kwargs.get("id")
        if chart_id is None:
            chart_id = uuid4()
        elif isinstance(chart_id, str):
            try:
                chart_id = UUID(chart_id)
            except ValueError:
                chart_id = uuid4()
        elif not isinstance(chart_id, UUID):
            chart_id = uuid4()

        client_id = kwargs.get("client_id")
        if client_id is None:
            client_id = uuid4()
        elif isinstance(client_id, str):
            try:
                client_id = UUID(client_id)
            except ValueError:
                client_id = uuid4()
        elif not isinstance(client_id, UUID):
            client_id = uuid4()

        chart_data = {
            "id": chart_id,
            "client_id": client_id,
            "data": kwargs.get("data", kwargs.get("chart_data", {})),  # Support both 'data' and 'chart_data'
            "solar_set": kwargs.get("solar_set", kwargs.get("solar_set_data", {})),  # Support both names
            "interpretations": kwargs.get("interpretations", {}),
            "house_system": kwargs.get("house_system", "placidus"),
            "calculated_at": kwargs.get("calculated_at", datetime.now(timezone.utc))
        }
        chart = NatalChartModel(**chart_data)
        db_session.add(chart)
        db_session.commit()
        db_session.refresh(chart)
        return chart

    return _create_chart


# ============================================================================
# Helper Fixtures
# ============================================================================

@pytest.fixture
def auth_headers(consultant_token: str) -> dict:
    """Generate authorization headers"""
    return {"Authorization": f"Bearer {consultant_token}"}


@pytest.fixture
def admin_headers(admin_token: str) -> dict:
    """Generate admin authorization headers"""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def authenticated_consultant(create_db_user, password_service: PasswordService, consultant_user, consultant_token: str):
    """Create consultant user in DB and return user + token"""
    db_user = create_db_user(
        id=str(consultant_user.id),
        email=consultant_user.email,
        hashed_password=password_service.hash_password("consultant123"),
        role="consultant",
        is_active=True
    )
    return {
        "user": db_user,
        "token": consultant_token,
        "headers": {"Authorization": f"Bearer {consultant_token}"}
    }


@pytest.fixture
def authenticated_admin(create_db_user, password_service: PasswordService, admin_user, admin_token: str):
    """Create admin user in DB and return user + token"""
    db_user = create_db_user(
        id=str(admin_user.id),
        email=admin_user.email,
        hashed_password=password_service.hash_password("admin123"),
        role="admin",
        is_active=True
    )
    return {
        "user": db_user,
        "token": admin_token,
        "headers": {"Authorization": f"Bearer {admin_token}"}
    }
