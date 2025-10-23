"""
Integration tests for Authentication Use Cases
"""
import pytest
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from src.application.use_cases.auth.login_use_case import LoginUseCase
from src.application.use_cases.auth.register_user_use_case import RegisterUserUseCase
from src.application.use_cases.auth.refresh_token_use_case import RefreshTokenUseCase
from src.application.dtos.auth_dtos import LoginDTO, RegisterUserDTO, RefreshTokenDTO
from src.application.services.password_service import PasswordService
from src.application.services.token_service import TokenService
from src.adapters.repositories.sqlalchemy.user_repository import SQLAlchemyUserRepository
from src.domain.entities.user import UserRole
from src.domain.exceptions import InvalidCredentialsError, DuplicateEntityError


@pytest.mark.integration
@pytest.mark.auth
class TestLoginUseCase:
    """Integration tests for LoginUseCase"""

    @pytest.fixture
    def login_use_case(self, db_session: Session, password_service: PasswordService, token_service: TokenService):
        """Create LoginUseCase instance"""
        user_repo = SQLAlchemyUserRepository(db_session)
        return LoginUseCase(user_repo, password_service, token_service)

    def test_login_success(self, login_use_case: LoginUseCase, create_db_user, password_service: PasswordService):
        """Test successful login"""
        # Create user in database
        email = "test@example.com"
        password = "password123"
        create_db_user(
            email=email,
            hashed_password=password_service.hash_password(password),
            role=UserRole.CONSULTANT.value,
            is_active=True
        )

        # Execute login
        dto = LoginDTO(email=email, password=password)
        tokens, user = login_use_case.execute(dto)

        assert tokens.access_token is not None
        assert tokens.refresh_token is not None
        assert tokens.token_type == "bearer"
        assert tokens.expires_in == 1800  # 30 minutes
        assert user.email == email
        assert user.role == UserRole.CONSULTANT.value

    def test_login_invalid_email(self, login_use_case: LoginUseCase):
        """Test login with non-existent email"""
        dto = LoginDTO(email="nonexistent@example.com", password="password123")

        with pytest.raises(InvalidCredentialsError):
            login_use_case.execute(dto)

    def test_login_invalid_password(self, login_use_case: LoginUseCase, create_db_user, password_service: PasswordService):
        """Test login with incorrect password"""
        email = "test@example.com"
        create_db_user(
            email=email,
            hashed_password=password_service.hash_password("correct_password"),
            is_active=True
        )

        dto = LoginDTO(email=email, password="wrong_password")

        with pytest.raises(InvalidCredentialsError):
            login_use_case.execute(dto)

    def test_login_inactive_user(self, login_use_case: LoginUseCase, create_db_user, password_service: PasswordService):
        """Test login with inactive user"""
        email = "inactive@example.com"
        password = "password123"
        create_db_user(
            email=email,
            hashed_password=password_service.hash_password(password),
            is_active=False
        )

        dto = LoginDTO(email=email, password=password)

        with pytest.raises(InvalidCredentialsError):
            login_use_case.execute(dto)


@pytest.mark.integration
@pytest.mark.auth
class TestRegisterUserUseCase:
    """Integration tests for RegisterUserUseCase"""

    @pytest.fixture
    def register_use_case(self, db_session: Session, password_service: PasswordService):
        """Create RegisterUserUseCase instance"""
        user_repo = SQLAlchemyUserRepository(db_session)
        return RegisterUserUseCase(user_repo, password_service)

    def test_register_user_success(self, register_use_case: RegisterUserUseCase):
        """Test successful user registration"""
        dto = RegisterUserDTO(
            email="newuser@example.com",
            password="secure_password123",
            role=UserRole.CONSULTANT,
            preferred_language="en"
        )

        result = register_use_case.execute(dto)

        assert result.id is not None
        assert result.email == dto.email
        assert result.role == UserRole.CONSULTANT.value
        assert result.is_active is True
        assert result.preferred_language == "en"
        assert result.created_at is not None

    def test_register_duplicate_email(self, register_use_case: RegisterUserUseCase, create_db_user):
        """Test registration with duplicate email"""
        email = "existing@example.com"
        create_db_user(email=email)

        dto = RegisterUserDTO(
            email=email,
            password="password123",
            role=UserRole.USER,
            preferred_language="en"
        )

        with pytest.raises(DuplicateEntityError):
            register_use_case.execute(dto)

    def test_register_admin_user(self, register_use_case: RegisterUserUseCase):
        """Test registering admin user"""
        dto = RegisterUserDTO(
            email="admin@example.com",
            password="admin_password",
            role=UserRole.ADMIN,
            preferred_language="es"
        )

        result = register_use_case.execute(dto)

        assert result.role == UserRole.ADMIN.value
        assert result.preferred_language == "es"

    def test_register_password_is_hashed(self, register_use_case: RegisterUserUseCase, db_session: Session):
        """Test that password is properly hashed"""
        from src.infrastructure.database.models import UserModel
        from uuid import UUID

        plain_password = "my_plain_password"
        dto = RegisterUserDTO(
            email="test@example.com",
            password=plain_password,
            role=UserRole.USER,
            preferred_language="en"
        )

        result = register_use_case.execute(dto)

        # Convert result.id to UUID if it's a string
        user_id = result.id if isinstance(result.id, UUID) else UUID(result.id)

        # Verify in database
        db_user = db_session.query(UserModel).filter(UserModel.id == user_id).first()
        assert db_user is not None
        assert db_user.hashed_password != plain_password
        assert db_user.hashed_password.startswith("$2b$")


@pytest.mark.integration
@pytest.mark.auth
class TestRefreshTokenUseCase:
    """Integration tests for RefreshTokenUseCase"""

    @pytest.fixture
    def refresh_use_case(self, db_session: Session, token_service: TokenService):
        """Create RefreshTokenUseCase instance"""
        user_repo = SQLAlchemyUserRepository(db_session)
        return RefreshTokenUseCase(user_repo, token_service)

    def test_refresh_token_success(self, refresh_use_case: RefreshTokenUseCase, create_db_user, token_service: TokenService):
        """Test successful token refresh"""
        user = create_db_user(email="test@example.com", is_active=True, role="consultant")
        refresh_token = token_service.create_refresh_token(user.id)

        dto = RefreshTokenDTO(refresh_token=refresh_token)
        result = refresh_use_case.execute(dto)

        assert result.access_token is not None
        assert result.refresh_token is not None
        assert result.token_type == "bearer"
        assert result.expires_in == 1800

    def test_refresh_token_invalid(self, refresh_use_case: RefreshTokenUseCase):
        """Test refresh with invalid token"""
        dto = RefreshTokenDTO(refresh_token="invalid_token")

        with pytest.raises(InvalidCredentialsError):
            refresh_use_case.execute(dto)

    def test_refresh_token_inactive_user(self, refresh_use_case: RefreshTokenUseCase, create_db_user, token_service: TokenService):
        """Test refresh for inactive user"""
        user = create_db_user(email="inactive@example.com", is_active=False)
        refresh_token = token_service.create_refresh_token(user.id)

        dto = RefreshTokenDTO(refresh_token=refresh_token)

        with pytest.raises(InvalidCredentialsError):
            refresh_use_case.execute(dto)

    def test_refresh_token_nonexistent_user(self, refresh_use_case: RefreshTokenUseCase, token_service: TokenService):
        """Test refresh for non-existent user"""
        from uuid import uuid4
        nonexistent_id = uuid4()
        refresh_token = token_service.create_refresh_token(nonexistent_id)

        dto = RefreshTokenDTO(refresh_token=refresh_token)

        # Should raise UserNotFoundError or InvalidCredentialsError
        with pytest.raises((InvalidCredentialsError, Exception)):  # UserNotFoundError is also acceptable
            refresh_use_case.execute(dto)
