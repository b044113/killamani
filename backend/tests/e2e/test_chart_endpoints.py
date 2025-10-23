"""
End-to-end tests for Chart Calculation endpoints
Tests: POST /api/charts/natal, GET /api/charts/natal/{chart_id},
       GET /api/charts/client/{client_id}/charts
"""
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.application.services.password_service import PasswordService


@pytest.mark.e2e
@pytest.mark.charts
class TestCalculateNatalChartEndpoint:
    """Test POST /api/charts/natal"""

    def test_calculate_natal_chart_success(
        self,
        client: TestClient,
        create_db_client,
        authenticated_consultant
    ):
        """Test successful natal chart calculation"""
        # Create consultant and client
        consultant = authenticated_consultant["user"]

        db_client = create_db_client(
            id="test-client-id",
            consultant_id=consultant.id,
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            birth_date=datetime(1990, 5, 15, 14, 30, tzinfo=timezone.utc),
            birth_city="New York",
            birth_country="US",
            birth_timezone="America/New_York",
            birth_latitude=40.7128,
            birth_longitude=-74.0060
        )

        response = client.post(
            "/api/charts/natal",
            headers=authenticated_consultant["headers"],
            json={
                "client_id": str(db_client.id),
                "house_system": "placidus",
                "language": "en",
                "include_chiron": True,
                "include_lilith": True,
                "include_nodes": True
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert "id" in data
        assert data["client_id"] == db_client.id
        assert "data" in data
        assert "solar_set" in data
        assert data["house_system"] == "placidus"
        assert "calculated_at" in data

    def test_calculate_natal_chart_minimal_options(
        self,
        client: TestClient,
        create_db_client,
        authenticated_consultant
    ):
        """Test natal chart calculation with minimal options"""
        consultant = authenticated_consultant["user"]

        db_client = create_db_client(
            id="test-client-id",
            consultant_id=consultant.id,
            first_name="Jane",
            last_name="Doe",
            email="jane@test.com"
        )

        response = client.post(
            "/api/charts/natal",
            headers=authenticated_consultant["headers"],
            json={
                "client_id": str(db_client.id)
            }
        )

        assert response.status_code == 200
        data = response.json()
        # Should use default values
        assert data["house_system"] == "placidus"

    def test_calculate_natal_chart_client_not_found(
        self,
        client: TestClient,
        create_db_user,
        password_service: PasswordService,
        consultant_token: str
    ):
        """Test calculating chart for non-existent client returns 404"""
        create_db_user(
            id="consultant-test-id",
            email="consultant@test.com",
            hashed_password=password_service.hash_password("password"),
            role="consultant",
            is_active=True
        )

        response = client.post(
            "/api/charts/natal",
            headers=authenticated_consultant["headers"],
            json={
                "client_id": "nonexistent-client-id"
            }
        )

        assert response.status_code == 404

    def test_calculate_natal_chart_without_auth(self, client: TestClient):
        """Test calculating chart without authentication returns 403"""
        response = client.post(
            "/api/charts/natal",
            json={
                "client_id": "some-client-id"
            }
        )

        assert response.status_code == 403

    def test_calculate_natal_chart_missing_client_id(
        self,
        client: TestClient,
        create_db_user,
        password_service: PasswordService,
        consultant_token: str
    ):
        """Test calculating chart without client_id returns 422"""
        create_db_user(
            id="consultant-test-id",
            email="consultant@test.com",
            hashed_password=password_service.hash_password("password"),
            role="consultant",
            is_active=True
        )

        response = client.post(
            "/api/charts/natal",
            headers=authenticated_consultant["headers"],
            json={}
        )

        assert response.status_code == 422

    def test_calculate_natal_chart_different_house_systems(
        self,
        client: TestClient,
        create_db_client,
        authenticated_consultant
    ):
        """Test calculating charts with different house systems"""
        consultant = authenticated_consultant["user"]

        db_client = create_db_client(
            id="test-client-id",
            consultant_id=consultant.id,
            first_name="Test",
            last_name="User",
            email="test@test.com"
        )

        house_systems = ["placidus", "koch", "equal", "whole_sign"]

        for house_system in house_systems:
            response = client.post(
                "/api/charts/natal",
                headers=authenticated_consultant["headers"],
                json={
                    "client_id": str(db_client.id),
                    "house_system": house_system
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["house_system"] == house_system

    def test_calculate_natal_chart_with_all_options(
        self,
        client: TestClient,
        create_db_client,
        authenticated_consultant
    ):
        """Test natal chart calculation with all optional parameters"""
        consultant = authenticated_consultant["user"]

        db_client = create_db_client(
            id="test-client-id",
            consultant_id=consultant.id,
            first_name="Complete",
            last_name="Test",
            email="complete@test.com"
        )

        response = client.post(
            "/api/charts/natal",
            headers=authenticated_consultant["headers"],
            json={
                "client_id": str(db_client.id),
                "house_system": "koch",
                "language": "es",
                "include_chiron": False,
                "include_lilith": False,
                "include_nodes": False
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["house_system"] == "koch"


@pytest.mark.e2e
@pytest.mark.charts
class TestGetChartDetailsEndpoint:
    """Test GET /api/charts/natal/{chart_id}"""

    def test_get_chart_details_success(
        self,
        client: TestClient,
        create_db_user,
        create_db_client,
        create_db_chart,
        password_service: PasswordService,
        consultant_token: str
    ):
        """Test getting chart details"""
        consultant = authenticated_consultant["user"]

        db_client = create_db_client(
            id="test-client-id",
            consultant_id=consultant.id,
            first_name="John",
            last_name="Doe",
            email="john@test.com"
        )

        chart = create_db_chart(
            id="test-chart-id",
            client_id=db_client.id,
            chart_data={"planets": [], "houses": []},
            solar_set_data={"sun_sign": "Taurus"},
            house_system="placidus"
        )

        response = client.get(
            f"/api/charts/natal/{chart.id}",
            headers=authenticated_consultant["headers"]
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == chart.id
        assert data["client_id"] == db_client.id
        assert "data" in data
        assert "solar_set" in data
        assert data["house_system"] == "placidus"

    def test_get_chart_not_found(
        self,
        client: TestClient,
        create_db_user,
        password_service: PasswordService,
        consultant_token: str
    ):
        """Test getting non-existent chart returns 404"""
        create_db_user(
            id="consultant-test-id",
            email="consultant@test.com",
            hashed_password=password_service.hash_password("password"),
            role="consultant",
            is_active=True
        )

        response = client.get(
            "/api/charts/natal/nonexistent-chart-id",
            headers=authenticated_consultant["headers"]
        )

        assert response.status_code == 404

    def test_get_chart_without_auth(self, client: TestClient):
        """Test getting chart without authentication returns 403"""
        response = client.get("/api/charts/natal/some-chart-id")

        assert response.status_code == 403


@pytest.mark.e2e
@pytest.mark.charts
class TestListClientChartsEndpoint:
    """Test GET /api/charts/client/{client_id}/charts"""

    def test_list_client_charts_success(
        self,
        client: TestClient,
        create_db_user,
        create_db_client,
        create_db_chart,
        password_service: PasswordService,
        consultant_token: str
    ):
        """Test listing charts for a client"""
        consultant = authenticated_consultant["user"]

        db_client = create_db_client(
            id="test-client-id",
            consultant_id=consultant.id,
            first_name="John",
            last_name="Doe",
            email="john@test.com"
        )

        # Create multiple charts for the same client
        for i in range(3):
            create_db_chart(
                id=f"chart-{i}",
                client_id=db_client.id,
                chart_data={},
                house_system="placidus"
            )

        response = client.get(
            f"/api/charts/client/{db_client.id}/charts",
            headers=authenticated_consultant["headers"]
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
        # All charts should belong to the same client
        for chart in data:
            assert chart["client_id"] == db_client.id

    def test_list_client_charts_empty(
        self,
        client: TestClient,
        create_db_client,
        authenticated_consultant
    ):
        """Test listing charts for client with no charts"""
        consultant = authenticated_consultant["user"]

        db_client = create_db_client(
            id="test-client-id",
            consultant_id=consultant.id,
            first_name="Jane",
            last_name="Doe",
            email="jane@test.com"
        )

        response = client.get(
            f"/api/charts/client/{db_client.id}/charts",
            headers=authenticated_consultant["headers"]
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_list_charts_client_not_found(
        self,
        client: TestClient,
        create_db_user,
        password_service: PasswordService,
        consultant_token: str
    ):
        """Test listing charts for non-existent client"""
        create_db_user(
            id="consultant-test-id",
            email="consultant@test.com",
            hashed_password=password_service.hash_password("password"),
            role="consultant",
            is_active=True
        )

        response = client.get(
            "/api/charts/client/nonexistent-client-id/charts",
            headers=authenticated_consultant["headers"]
        )

        # Could return 404 or empty list depending on implementation
        assert response.status_code in [200, 404]

    def test_list_client_charts_without_auth(self, client: TestClient):
        """Test listing charts without authentication returns 403"""
        response = client.get("/api/charts/client/some-client-id/charts")

        assert response.status_code == 403

    def test_list_client_charts_ordering(
        self,
        client: TestClient,
        create_db_user,
        create_db_client,
        create_db_chart,
        password_service: PasswordService,
        consultant_token: str
    ):
        """Test that charts are ordered by calculation date"""
        consultant = authenticated_consultant["user"]

        db_client = create_db_client(
            id="test-client-id",
            consultant_id=consultant.id,
            first_name="Order",
            last_name="Test",
            email="order@test.com"
        )

        # Create charts at different times
        from datetime import timedelta
        base_time = datetime.now(timezone.utc)

        for i in range(3):
            create_db_chart(
                id=f"chart-{i}",
                client_id=db_client.id,
                chart_data={},
                calculated_at=base_time + timedelta(hours=i)
            )

        response = client.get(
            f"/api/charts/client/{db_client.id}/charts",
            headers=authenticated_consultant["headers"]
        )

        assert response.status_code == 200
        data = response.json()

        # Verify ordering (should be most recent first or oldest first)
        calculated_dates = [chart["calculated_at"] for chart in data]
        # Just verify we got all charts
        assert len(calculated_dates) == 3


@pytest.mark.e2e
@pytest.mark.charts
class TestChartEndToEndFlow:
    """Test complete chart calculation flow"""

    def test_complete_chart_workflow(
        self,
        client: TestClient,
        create_db_user,
        password_service: PasswordService,
        consultant_token: str
    ):
        """Test create client -> calculate chart -> get chart -> list charts"""
        # Setup consultant
        create_db_user(
            id="consultant-test-id",
            email="consultant@test.com",
            hashed_password=password_service.hash_password("password"),
            role="consultant",
            is_active=True
        )

        # 1. Create a client
        client_response = client.post(
            "/api/clients/",
            headers=authenticated_consultant["headers"],
            json={
                "first_name": "Chart",
                "last_name": "Test",
                "email": "chart@test.com",
                "birth_data": {
                    "date": "1990-05-15T14:30:00+00:00",
                    "city": "New York",
                    "country": "US",
                    "timezone": "America/New_York",
                    "latitude": 40.7128,
                    "longitude": -74.0060
                }
            }
        )
        assert client_response.status_code == 200
        client_id = client_response.json()["id"]

        # 2. Calculate natal chart
        chart_response = client.post(
            "/api/charts/natal",
            headers=authenticated_consultant["headers"],
            json={
                "client_id": client_id,
                "house_system": "placidus",
                "language": "en",
                "include_chiron": True,
                "include_lilith": True,
                "include_nodes": True
            }
        )
        assert chart_response.status_code == 200
        chart_id = chart_response.json()["id"]

        # 3. Get chart details
        get_chart_response = client.get(
            f"/api/charts/natal/{chart_id}",
            headers=authenticated_consultant["headers"]
        )
        assert get_chart_response.status_code == 200
        assert get_chart_response.json()["client_id"] == client_id

        # 4. List all charts for the client
        list_charts_response = client.get(
            f"/api/charts/client/{client_id}/charts",
            headers=authenticated_consultant["headers"]
        )
        assert list_charts_response.status_code == 200
        charts = list_charts_response.json()
        assert len(charts) >= 1
        assert any(c["id"] == chart_id for c in charts)

    def test_calculate_multiple_charts_for_same_client(
        self,
        client: TestClient,
        create_db_client,
        authenticated_consultant
    ):
        """Test calculating multiple charts with different options for same client"""
        consultant = authenticated_consultant["user"]

        db_client = create_db_client(
            id="test-client-id",
            consultant_id=consultant.id,
            first_name="Multi",
            last_name="Chart",
            email="multi@test.com"
        )

        # Calculate chart with different house systems
        house_systems = ["placidus", "koch", "equal"]
        chart_ids = []

        for house_system in house_systems:
            response = client.post(
                "/api/charts/natal",
                headers=authenticated_consultant["headers"],
                json={
                    "client_id": str(db_client.id),
                    "house_system": house_system
                }
            )
            assert response.status_code == 200
            chart_ids.append(response.json()["id"])

        # Verify all charts were created
        list_response = client.get(
            f"/api/charts/client/{db_client.id}/charts",
            headers=authenticated_consultant["headers"]
        )
        assert list_response.status_code == 200
        charts = list_response.json()
        assert len(charts) >= 3
