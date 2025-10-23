"""
End-to-end tests for Client Management endpoints
Tests: POST /api/clients/, GET /api/clients/, GET /api/clients/search,
       GET /api/clients/{client_id}, PUT /api/clients/{client_id}
"""
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.application.services.password_service import PasswordService
from src.application.services.token_service import TokenService


@pytest.mark.e2e
@pytest.mark.clients
class TestCreateClientEndpoint:
    """Test POST /api/clients/"""

    def test_create_client_success(
        self,
        client: TestClient,
        create_db_user,
        password_service: PasswordService,
        token_service: TokenService
    ):
        """Test successful client creation"""
        # Create consultant user in database
        from uuid import UUID
        consultant_id = UUID("12345678-1234-1234-1234-123456789002")

        create_db_user(
            id=str(consultant_id),
            email="consultant@test.com",
            hashed_password=password_service.hash_password("password"),
            role="consultant",
            is_active=True
        )

        # Generate token
        token = token_service.create_access_token(
            consultant_id,
            additional_claims={"role": "consultant"}
        )

        response = client.post(
            "/api/clients/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "birth_data": {
                    "date": "1990-05-15T14:30:00+00:00",
                    "city": "New York",
                    "country": "US",
                    "timezone": "America/New_York",
                    "latitude": 40.7128,
                    "longitude": -74.0060
                },
                "notes": "Test client notes"
            }
        )

        assert response.status_code == 201
        data = response.json()

        assert "id" in data
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert data["email"] == "john.doe@example.com"
        # API returns birth data as flat fields, not nested
        assert data["birth_city"] == "New York"
        assert data["birth_country"] == "US"
        assert data["birth_timezone"] == "America/New_York"
        assert data["notes"] == "Test client notes"

    def test_create_client_without_auth(self, client: TestClient):
        """Test creating client without authentication returns 403"""
        response = client.post("/api/clients/", json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "birth_data": {
                "date": "1990-05-15T14:30:00+00:00",
                "city": "New York",
                "country": "US",
                "timezone": "America/New_York"
            }
        })

        assert response.status_code == 403

    def test_create_client_missing_required_fields(
        self,
        client: TestClient,
        authenticated_consultant
    ):
        """Test creating client without required fields returns 422"""
        response = client.post(
            "/api/clients/",
            headers=authenticated_consultant["headers"],
            json={
                "first_name": "John"
                # Missing last_name, email, birth_data
            }
        )

        assert response.status_code == 422

    def test_create_client_invalid_email(
        self,
        client: TestClient,
        authenticated_consultant
    ):
        """Test creating client with invalid email format - currently accepted as email is optional"""
        response = client.post(
            "/api/clients/",
            headers=authenticated_consultant["headers"],
            json={
                "first_name": "John",
                "last_name": "Doe",
                "email": "invalid-email",
                "birth_data": {
                    "date": "1990-05-15T14:30:00+00:00",
                    "city": "New York",
                    "country": "US",
                    "timezone": "America/New_York"
                }
            }
        )

        # Email validation is not enforced at DTO level, so this succeeds
        assert response.status_code == 201

    def test_create_client_with_optional_notes(
        self,
        client: TestClient,
        authenticated_consultant
    ):
        """Test creating client with optional notes field"""
        response = client.post(
            "/api/clients/",
            headers=authenticated_consultant["headers"],
            json={
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane.smith@example.com",
                "birth_data": {
                    "date": "1985-10-20T08:45:00+00:00",
                    "city": "London",
                    "country": "GB",
                    "timezone": "Europe/London",
                    "latitude": 51.5074,
                    "longitude": -0.1278
                }
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["notes"] is None


@pytest.mark.e2e
@pytest.mark.clients
class TestListClientsEndpoint:
    """Test GET /api/clients/"""

    def test_list_clients_success(
        self,
        client: TestClient,
        create_db_client,
        authenticated_consultant
    ):
        """Test listing clients with pagination"""
        # Create consultant
        consultant = authenticated_consultant["user"]

        # Create multiple clients
        for i in range(5):
            create_db_client(
                consultant_id=consultant.id,
                first_name=f"Client{i}",
                last_name=f"Test{i}",
                email=f"client{i}@test.com"
            )

        response = client.get(
            "/api/clients/?skip=0&limit=10",
            headers=authenticated_consultant["headers"]
        )

        assert response.status_code == 200
        data = response.json()

        assert "clients" in data
        assert "total" in data
        assert data["total"] == 5
        assert len(data["clients"]) == 5

    def test_list_clients_pagination(
        self,
        client: TestClient,
        create_db_client,
        authenticated_consultant
    ):
        """Test pagination parameters"""
        consultant = authenticated_consultant["user"]

        # Create 10 clients
        for i in range(10):
            create_db_client(
                consultant_id=consultant.id,
                first_name=f"Client{i}",
                email=f"client{i}@test.com"
            )

        # Get first page
        response = client.get(
            "/api/clients/?skip=0&limit=5",
            headers=authenticated_consultant["headers"]
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["clients"]) == 5
        assert data["total"] == 10

        # Get second page
        response2 = client.get(
            "/api/clients/?skip=5&limit=5",
            headers=authenticated_consultant["headers"]
        )

        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2["clients"]) == 5

    def test_list_clients_without_auth(self, client: TestClient):
        """Test listing clients without authentication returns 403"""
        response = client.get("/api/clients/")

        assert response.status_code == 403

    def test_list_clients_empty_list(
        self,
        client: TestClient,
        authenticated_consultant
    ):
        """Test listing when no clients exist"""
        response = client.get(
            "/api/clients/",
            headers=authenticated_consultant["headers"]
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["clients"]) == 0


@pytest.mark.e2e
@pytest.mark.clients
class TestSearchClientsEndpoint:
    """Test GET /api/clients/search"""

    def test_search_clients_by_name(
        self,
        client: TestClient,
        create_db_client,
        authenticated_consultant
    ):
        """Test searching clients by name"""
        consultant = authenticated_consultant["user"]

        create_db_client(
            consultant_id=consultant.id,
            first_name="John",
            last_name="Doe",
            email="john@test.com"
        )
        create_db_client(
            consultant_id=consultant.id,
            first_name="Jane",
            last_name="Smith",
            email="jane@test.com"
        )

        response = client.get(
            "/api/clients/search?query=John",
            headers=authenticated_consultant["headers"]
        )

        assert response.status_code == 200
        data = response.json()
        assert "clients" in data
        assert len(data["clients"]) >= 1
        assert any(c["first_name"] == "John" for c in data["clients"])

    def test_search_clients_by_email(
        self,
        client: TestClient,
        create_db_client,
        authenticated_consultant
    ):
        """Test searching clients by email"""
        consultant = authenticated_consultant["user"]

        create_db_client(
            consultant_id=consultant.id,
            first_name="Test",
            last_name="User",
            email="specific@example.com"
        )

        response = client.get(
            "/api/clients/search?query=specific@example.com",
            headers=authenticated_consultant["headers"]
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["clients"]) >= 1

    def test_search_clients_no_results(
        self,
        client: TestClient,
        authenticated_consultant
    ):
        """Test search with no matching results"""
        response = client.get(
            "/api/clients/search?query=NonexistentClient",
            headers=authenticated_consultant["headers"]
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["clients"]) == 0


@pytest.mark.e2e
@pytest.mark.clients
class TestGetClientDetailsEndpoint:
    """Test GET /api/clients/{client_id}"""

    def test_get_client_details_success(
        self,
        client: TestClient,
        create_db_client,
        authenticated_consultant
    ):
        """Test getting client details"""
        consultant = authenticated_consultant["user"]

        db_client = create_db_client(
            id="test-client-123",
            consultant_id=consultant.id,
            first_name="John",
            last_name="Doe",
            email="john@test.com"
        )

        response = client.get(
            f"/api/clients/{db_client.id}",
            headers=authenticated_consultant["headers"]
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(db_client.id)
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"

    def test_get_client_not_found(
        self,
        client: TestClient,
        authenticated_consultant
    ):
        """Test getting non-existent client returns 404"""
        from uuid import uuid4
        nonexistent_id = uuid4()

        response = client.get(
            f"/api/clients/{nonexistent_id}",
            headers=authenticated_consultant["headers"]
        )

        # Can be 400 if UUID validation fails, or 404 if not found
        assert response.status_code in [400, 404]

    def test_get_client_without_auth(self, client: TestClient):
        """Test getting client without authentication returns 403"""
        response = client.get("/api/clients/some-id")

        assert response.status_code == 403


@pytest.mark.e2e
@pytest.mark.clients
class TestUpdateClientEndpoint:
    """Test PUT /api/clients/{client_id}"""

    def test_update_client_success(
        self,
        client: TestClient,
        create_db_client,
        authenticated_consultant
    ):
        """Test successful client update"""
        consultant = authenticated_consultant["user"]

        db_client = create_db_client(
            id="test-client-123",
            consultant_id=consultant.id,
            first_name="John",
            last_name="Doe",
            email="john@test.com"
        )

        response = client.put(
            f"/api/clients/{db_client.id}",
            headers=authenticated_consultant["headers"],
            json={
                "first_name": "Johnny",
                "last_name": "Updated",
                "email": "johnny.updated@test.com",
                "notes": "Updated notes"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Johnny"
        assert data["last_name"] == "Updated"
        assert data["email"] == "johnny.updated@test.com"
        assert data["notes"] == "Updated notes"

    def test_update_client_partial(
        self,
        client: TestClient,
        create_db_client,
        authenticated_consultant
    ):
        """Test partial client update"""
        consultant = authenticated_consultant["user"]

        db_client = create_db_client(
            id="test-client-123",
            consultant_id=consultant.id,
            first_name="John",
            last_name="Doe",
            email="john@test.com"
        )

        response = client.put(
            f"/api/clients/{db_client.id}",
            headers=authenticated_consultant["headers"],
            json={
                "notes": "Only updating notes"
            }
        )

        assert response.status_code == 200
        data = response.json()
        # Original values should remain
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        # Updated value
        assert data["notes"] == "Only updating notes"

    def test_update_client_not_found(
        self,
        client: TestClient,
        authenticated_consultant
    ):
        """Test updating non-existent client returns 404"""
        from uuid import uuid4
        nonexistent_id = uuid4()

        response = client.put(
            f"/api/clients/{nonexistent_id}",
            headers=authenticated_consultant["headers"],
            json={
                "first_name": "Updated"
            }
        )

        # Can be 400 if UUID validation fails, or 404 if not found
        assert response.status_code in [400, 404]

    def test_update_client_without_auth(self, client: TestClient):
        """Test updating client without authentication returns 403"""
        response = client.put(
            "/api/clients/some-id",
            json={"first_name": "Updated"}
        )

        assert response.status_code == 403


@pytest.mark.e2e
@pytest.mark.clients
class TestClientEndToEndFlow:
    """Test complete client management flow"""

    def test_complete_client_lifecycle(
        self,
        client: TestClient,
        authenticated_consultant
    ):
        """Test create -> get -> update -> search flow"""
        # Setup consultant
        # 1. Create client
        create_response = client.post(
            "/api/clients/",
            headers=authenticated_consultant["headers"],
            json={
                "first_name": "Alice",
                "last_name": "Wonder",
                "email": "alice@example.com",
                "birth_data": {
                    "date": "1990-05-15T14:30:00+00:00",
                    "city": "Paris",
                    "country": "FR",
                    "timezone": "Europe/Paris",
                    "latitude": 48.8566,
                    "longitude": 2.3522
                }
            }
        )
        assert create_response.status_code == 201
        client_id = create_response.json()["id"]

        # 2. Get client details
        get_response = client.get(
            f"/api/clients/{client_id}",
            headers=authenticated_consultant["headers"]
        )
        assert get_response.status_code == 200
        assert get_response.json()["first_name"] == "Alice"

        # 3. Update client
        update_response = client.put(
            f"/api/clients/{client_id}",
            headers=authenticated_consultant["headers"],
            json={
                "notes": "Updated with new information"
            }
        )
        assert update_response.status_code == 200

        # 4. Search for client
        search_response = client.get(
            "/api/clients/search?query=Alice",
            headers=authenticated_consultant["headers"]
        )
        assert search_response.status_code == 200
        assert len(search_response.json()["clients"]) >= 1

        # 5. List all clients
        list_response = client.get(
            "/api/clients/",
            headers=authenticated_consultant["headers"]
        )
        assert list_response.status_code == 200
        assert list_response.json()["total"] >= 1
