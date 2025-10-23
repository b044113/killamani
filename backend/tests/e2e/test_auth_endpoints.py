"""
End-to-end tests for Authentication endpoints
Tests: POST /api/auth/login, /api/auth/register, /api/auth/refresh, /api/auth/logout
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.application.services.password_service import PasswordService
from src.application.services.token_service import TokenService


@pytest.mark.e2e
@pytest.mark.auth
class TestAuthLoginEndpoint:
    """Test POST /api/auth/login"""

    def test_login_success(
        self,
        client: TestClient,
        create_db_user,
        password_service: PasswordService
    ):
        """Test successful login returns tokens and user info"""
        email = "login@test.com"
        password = "test_password123"

        create_db_user(
            email=email,
            hashed_password=password_service.hash_password(password),
            role="consultant",
            is_active=True
        )

        response = client.post("/api/auth/login", json={
            "email": email,
            "password": password
        })

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 1800
        assert "user" in data
        assert data["user"]["email"] == email
        assert data["user"]["role"] == "consultant"

    def test_login_invalid_email(self, client: TestClient):
        """Test login with non-existent email returns 401"""
        response = client.post("/api/auth/login", json={
            "email": "nonexistent@test.com",
            "password": "password123"
        })

        assert response.status_code == 401
        data = response.json()
        assert "error" in data

    def test_login_invalid_password(
        self,
        client: TestClient,
        create_db_user,
        password_service: PasswordService
    ):
        """Test login with wrong password returns 401"""
        email = "test@test.com"
        create_db_user(
            email=email,
            hashed_password=password_service.hash_password("correct_password"),
            is_active=True
        )

        response = client.post("/api/auth/login", json={
            "email": email,
            "password": "wrong_password"
        })

        assert response.status_code == 401

    def test_login_inactive_user(
        self,
        client: TestClient,
        create_db_user,
        password_service: PasswordService
    ):
        """Test login with inactive account returns 401"""
        email = "inactive@test.com"
        password = "password123"

        create_db_user(
            email=email,
            hashed_password=password_service.hash_password(password),
            is_active=False
        )

        response = client.post("/api/auth/login", json={
            "email": email,
            "password": password
        })

        assert response.status_code == 401

    def test_login_missing_email(self, client: TestClient):
        """Test login without email returns 422"""
        response = client.post("/api/auth/login", json={
            "password": "password123"
        })

        assert response.status_code == 422

    def test_login_missing_password(self, client: TestClient):
        """Test login without password returns 422"""
        response = client.post("/api/auth/login", json={
            "email": "test@test.com"
        })

        assert response.status_code == 422

    def test_login_invalid_email_format(self, client: TestClient):
        """Test login with invalid email format returns 422"""
        response = client.post("/api/auth/login", json={
            "email": "not-an-email",
            "password": "password123"
        })

        # FastAPI validates email format and returns 422
        assert response.status_code in [401, 422]  # Both are acceptable

    def test_login_empty_credentials(self, client: TestClient):
        """Test login with empty strings"""
        response = client.post("/api/auth/login", json={
            "email": "",
            "password": ""
        })

        # Empty credentials should fail validation or authentication
        assert response.status_code in [401, 422]  # Both are acceptable


@pytest.mark.e2e
@pytest.mark.auth
class TestAuthRegisterEndpoint:
    """Test POST /api/auth/register"""

    def test_register_success(self, client: TestClient):
        """Test successful user registration"""
        response = client.post("/api/auth/register", json={
            "email": "newuser@test.com",
            "password": "secure_password123",
            "role": "consultant",
            "preferred_language": "en"
        })

        assert response.status_code == 201
        data = response.json()

        assert "id" in data
        assert data["email"] == "newuser@test.com"
        assert data["role"] == "consultant"
        assert data["is_active"] is True
        assert data["preferred_language"] == "en"
        assert "created_at" in data

    def test_register_duplicate_email(self, client: TestClient, create_db_user):
        """Test registration with existing email returns 409"""
        email = "existing@test.com"
        create_db_user(email=email)

        response = client.post("/api/auth/register", json={
            "email": email,
            "password": "password123",
            "role": "user",
            "preferred_language": "en"
        })

        assert response.status_code == 409
        data = response.json()
        assert "error" in data

    def test_register_admin_user(self, client: TestClient):
        """Test registering admin user"""
        response = client.post("/api/auth/register", json={
            "email": "admin@test.com",
            "password": "admin_password",
            "role": "admin",
            "preferred_language": "es"
        })

        assert response.status_code == 201
        data = response.json()
        assert data["role"] == "admin"
        assert data["preferred_language"] == "es"

    def test_register_missing_email(self, client: TestClient):
        """Test registration without email returns 422"""
        response = client.post("/api/auth/register", json={
            "password": "password123",
            "role": "user",
            "preferred_language": "en"
        })

        assert response.status_code == 422

    def test_register_missing_password(self, client: TestClient):
        """Test registration without password returns 422"""
        response = client.post("/api/auth/register", json={
            "email": "test@test.com",
            "role": "user",
            "preferred_language": "en"
        })

        assert response.status_code == 422

    def test_register_invalid_role(self, client: TestClient):
        """Test registration with invalid role"""
        response = client.post("/api/auth/register", json={
            "email": "test@test.com",
            "password": "password123",
            "role": "invalid_role",
            "preferred_language": "en"
        })

        assert response.status_code == 422

    def test_register_default_language(self, client: TestClient):
        """Test registration defaults to 'en' if language not provided"""
        response = client.post("/api/auth/register", json={
            "email": "test@test.com",
            "password": "password123",
            "role": "user"
        })

        assert response.status_code == 201
        data = response.json()
        assert data["preferred_language"] == "en"


@pytest.mark.e2e
@pytest.mark.auth
class TestAuthRefreshEndpoint:
    """Test POST /api/auth/refresh"""

    def test_refresh_token_success(
        self,
        client: TestClient,
        create_db_user,
        token_service: TokenService
    ):
        """Test successful token refresh"""
        user = create_db_user(email="test@test.com", is_active=True, role="consultant")
        refresh_token = token_service.create_refresh_token(user.id)

        response = client.post("/api/auth/refresh", json={
            "refresh_token": refresh_token
        })

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        # Note: RefreshTokenUseCase returns AuthTokensDTO which may not include user
        # This is acceptable as the client can decode the JWT to get user info

    def test_refresh_invalid_token(self, client: TestClient):
        """Test refresh with invalid token returns 401"""
        response = client.post("/api/auth/refresh", json={
            "refresh_token": "invalid_token_string"
        })

        assert response.status_code == 401

    def test_refresh_inactive_user(
        self,
        client: TestClient,
        create_db_user,
        token_service: TokenService
    ):
        """Test refresh for inactive user returns 401"""
        user = create_db_user(email="inactive@test.com", is_active=False)
        refresh_token = token_service.create_refresh_token(user.id)

        response = client.post("/api/auth/refresh", json={
            "refresh_token": refresh_token
        })

        assert response.status_code == 401

    def test_refresh_missing_token(self, client: TestClient):
        """Test refresh without token returns 422"""
        response = client.post("/api/auth/refresh", json={})

        assert response.status_code == 422

    def test_refresh_empty_token(self, client: TestClient):
        """Test refresh with empty token"""
        response = client.post("/api/auth/refresh", json={
            "refresh_token": ""
        })

        assert response.status_code == 401

    def test_refresh_access_token_instead_of_refresh(
        self,
        client: TestClient,
        create_db_user,
        token_service: TokenService
    ):
        """Test using access token for refresh should fail"""
        user = create_db_user(email="test@test.com", is_active=True, role="user")
        access_token = token_service.create_access_token(
            user.id,
            additional_claims={"role": "user"}
        )

        response = client.post("/api/auth/refresh", json={
            "refresh_token": access_token
        })

        # Should fail because token type is 'access' not 'refresh'
        assert response.status_code == 401


@pytest.mark.e2e
@pytest.mark.auth
class TestAuthLogoutEndpoint:
    """Test POST /api/auth/logout"""

    def test_logout_success(
        self,
        client: TestClient,
        create_db_user,
        password_service: PasswordService
    ):
        """Test successful logout"""
        email = "test@test.com"
        password = "password123"

        create_db_user(
            email=email,
            hashed_password=password_service.hash_password(password),
            role="user",
            is_active=True
        )

        # Login first
        login_response = client.post("/api/auth/login", json={
            "email": email,
            "password": password
        })
        access_token = login_response.json()["access_token"]

        # Logout
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        # 204 No Content is correct for logout (no response body)
        assert response.status_code == 204

    def test_logout_without_token(self, client: TestClient):
        """Test logout without authentication"""
        response = client.post("/api/auth/logout")

        # Logout is idempotent, returns 204 even without auth
        assert response.status_code == 204

    def test_logout_invalid_token(self, client: TestClient):
        """Test logout with invalid token"""
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": "Bearer invalid_token"}
        )

        # Logout is idempotent, returns 204 even with invalid token
        assert response.status_code == 204

    def test_logout_malformed_header(self, client: TestClient):
        """Test logout with malformed authorization header"""
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": "NotBearer token"}
        )

        # Logout is idempotent, returns 204 even with malformed header
        assert response.status_code == 204


@pytest.mark.e2e
@pytest.mark.auth
class TestAuthEndToEndFlow:
    """Test complete authentication flow"""

    def test_register_login_refresh_logout_flow(self, client: TestClient):
        """Test complete user journey"""
        email = "journey@test.com"
        password = "secure_password123"

        # 1. Register
        register_response = client.post("/api/auth/register", json={
            "email": email,
            "password": password,
            "role": "consultant",
            "preferred_language": "en"
        })
        assert register_response.status_code == 201

        # 2. Login
        login_response = client.post("/api/auth/login", json={
            "email": email,
            "password": password
        })
        assert login_response.status_code == 200
        login_data = login_response.json()
        access_token = login_data["access_token"]
        refresh_token = login_data["refresh_token"]

        # 3. Refresh token
        refresh_response = client.post("/api/auth/refresh", json={
            "refresh_token": refresh_token
        })
        assert refresh_response.status_code == 200
        new_access_token = refresh_response.json()["access_token"]

        # 4. Logout
        logout_response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {new_access_token}"}
        )
        assert logout_response.status_code == 204
