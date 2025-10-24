"""
End-to-End Tests for Quick Chart Calculation Endpoint

Tests the /api/charts/quick-calculate endpoint.
"""
import pytest
from fastapi.testclient import TestClient


class TestQuickChartEndpoint:
    """Test suite for quick chart calculation endpoint"""

    @pytest.fixture
    def valid_chart_data(self):
        """Valid chart calculation request data"""
        return {
            "name": "John Doe",
            "birth_date": "1990-04-15",
            "birth_time": "14:30",
            "birth_city": "New York",
            "birth_country": "US",
            "birth_timezone": "America/New_York",
            "birth_latitude": 40.7128,
            "birth_longitude": -74.0060,
            "include_chiron": True,
            "include_lilith": True,
            "include_nodes": True,
            "house_system": "placidus",
            "language": "en"
        }

    def test_quick_calculate_success(self, client: TestClient, valid_chart_data):
        """Test successful quick chart calculation"""
        # Act
        response = client.post("/api/charts/quick-calculate", json=valid_chart_data)

        # Assert
        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "John Doe"
        assert "sun_sign" in data
        assert "planets" in data
        assert "houses" in data
        assert "aspects" in data
        assert "angles" in data
        assert "solar_set" in data
        assert "svg_data" in data
        assert "calculated_at" in data

        # Verify SVG content
        assert "<svg" in data["svg_data"]

        # Verify planets data structure
        assert isinstance(data["planets"], list)
        assert len(data["planets"]) > 0

        # Verify houses data structure
        assert isinstance(data["houses"], list)
        assert len(data["houses"]) == 12

    def test_quick_calculate_minimal_data(self, client: TestClient):
        """Test with minimal required data (no coordinates)"""
        # Arrange
        minimal_data = {
            "name": "Jane Smith",
            "birth_date": "1985-12-25",
            "birth_time": "08:00",
            "birth_city": "London",
            "birth_country": "GB",
            "birth_timezone": "Europe/London"
        }

        # Act
        response = client.post("/api/charts/quick-calculate", json=minimal_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Jane Smith"

    def test_quick_calculate_no_authentication_required(self, client: TestClient, valid_chart_data):
        """Test that endpoint doesn't require authentication"""
        # Act - send request without authorization header
        response = client.post("/api/charts/quick-calculate", json=valid_chart_data)

        # Assert - should succeed without auth
        assert response.status_code == 200

    def test_quick_calculate_missing_required_fields(self, client: TestClient):
        """Test with missing required fields"""
        # Arrange - missing birth_time
        incomplete_data = {
            "name": "Test",
            "birth_date": "1990-04-15",
            "birth_city": "New York",
            "birth_country": "US",
            "birth_timezone": "America/New_York"
        }

        # Act
        response = client.post("/api/charts/quick-calculate", json=incomplete_data)

        # Assert
        assert response.status_code == 422  # Validation error

    def test_quick_calculate_invalid_date_format(self, client: TestClient):
        """Test with invalid date format"""
        # Arrange
        invalid_data = {
            "name": "Test",
            "birth_date": "15-04-1990",  # Wrong format
            "birth_time": "14:30",
            "birth_city": "New York",
            "birth_country": "US",
            "birth_timezone": "America/New_York"
        }

        # Act
        response = client.post("/api/charts/quick-calculate", json=invalid_data)

        # Assert
        assert response.status_code in [400, 422, 500]

    def test_quick_calculate_invalid_time_format(self, client: TestClient):
        """Test with invalid time format"""
        # Arrange
        invalid_data = {
            "name": "Test",
            "birth_date": "1990-04-15",
            "birth_time": "2:30 PM",  # Wrong format
            "birth_city": "New York",
            "birth_country": "US",
            "birth_timezone": "America/New_York"
        }

        # Act
        response = client.post("/api/charts/quick-calculate", json=invalid_data)

        # Assert
        assert response.status_code in [400, 422, 500]

    def test_quick_calculate_invalid_coordinates(self, client: TestClient):
        """Test with invalid latitude/longitude"""
        # Arrange
        invalid_data = {
            "name": "Test",
            "birth_date": "1990-04-15",
            "birth_time": "14:30",
            "birth_city": "New York",
            "birth_country": "US",
            "birth_timezone": "America/New_York",
            "birth_latitude": 999.0,  # Invalid
            "birth_longitude": -74.0060
        }

        # Act
        response = client.post("/api/charts/quick-calculate", json=invalid_data)

        # Assert
        assert response.status_code in [400, 422, 500]

    def test_quick_calculate_different_house_systems(self, client: TestClient):
        """Test calculation with different house systems"""
        house_systems = ["placidus", "koch", "equal", "whole_sign"]

        for house_system in house_systems:
            # Arrange
            data = {
                "name": "Test",
                "birth_date": "1990-04-15",
                "birth_time": "14:30",
                "birth_city": "New York",
                "birth_country": "US",
                "birth_timezone": "America/New_York",
                "house_system": house_system
            }

            # Act
            response = client.post("/api/charts/quick-calculate", json=data)

            # Assert
            assert response.status_code == 200
            result = response.json()
            assert result["house_system"] == house_system

    def test_quick_calculate_different_languages(self, client: TestClient):
        """Test calculation with different languages"""
        languages = ["en", "es", "it", "fr", "de", "pt"]

        for language in languages:
            # Arrange
            data = {
                "name": "Test",
                "birth_date": "1990-04-15",
                "birth_time": "14:30",
                "birth_city": "New York",
                "birth_country": "US",
                "birth_timezone": "America/New_York",
                "language": language
            }

            # Act
            response = client.post("/api/charts/quick-calculate", json=data)

            # Assert
            assert response.status_code == 200

    def test_quick_calculate_with_optional_bodies_disabled(self, client: TestClient):
        """Test calculation with optional bodies disabled"""
        # Arrange
        data = {
            "name": "Test",
            "birth_date": "1990-04-15",
            "birth_time": "14:30",
            "birth_city": "New York",
            "birth_country": "US",
            "birth_timezone": "America/New_York",
            "include_chiron": False,
            "include_lilith": False,
            "include_nodes": False
        }

        # Act
        response = client.post("/api/charts/quick-calculate", json=data)

        # Assert
        assert response.status_code == 200

    def test_quick_calculate_response_structure(self, client: TestClient, valid_chart_data):
        """Test that response has correct structure"""
        # Act
        response = client.post("/api/charts/quick-calculate", json=valid_chart_data)

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Required fields
        required_fields = [
            "name",
            "sun_sign",
            "planets",
            "houses",
            "aspects",
            "angles",
            "solar_set",
            "svg_data",
            "house_system",
            "calculated_at"
        ]

        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

        # Check data types
        assert isinstance(data["name"], str)
        assert isinstance(data["sun_sign"], str)
        assert isinstance(data["planets"], list)
        assert isinstance(data["houses"], list)
        assert isinstance(data["aspects"], list)
        assert isinstance(data["angles"], dict)
        assert isinstance(data["solar_set"], dict)
        assert isinstance(data["svg_data"], str)
        assert isinstance(data["house_system"], str)
        assert isinstance(data["calculated_at"], str)

    def test_quick_calculate_solar_set_content(self, client: TestClient, valid_chart_data):
        """Test that solar set contains expected data"""
        # Act
        response = client.post("/api/charts/quick-calculate", json=valid_chart_data)

        # Assert
        assert response.status_code == 200
        solar_set = response.json()["solar_set"]

        # Solar set should contain these fields
        assert "sun_sign" in solar_set
        assert "sun_house" in solar_set
        assert "sun_degree" in solar_set
        assert "fifth_house_sign" in solar_set
        assert "hard_aspects" in solar_set

    def test_quick_calculate_planets_content(self, client: TestClient, valid_chart_data):
        """Test that planets data contains expected information"""
        # Act
        response = client.post("/api/charts/quick-calculate", json=valid_chart_data)

        # Assert
        assert response.status_code == 200
        planets = response.json()["planets"]

        assert len(planets) >= 10  # At least 10 main planets

        # Check structure of first planet
        if len(planets) > 0:
            planet = planets[0]
            assert "name" in planet
            assert "sign" in planet
            assert "degree" in planet or "longitude" in planet
            assert "house" in planet

    def test_quick_calculate_houses_content(self, client: TestClient, valid_chart_data):
        """Test that houses data contains expected information"""
        # Act
        response = client.post("/api/charts/quick-calculate", json=valid_chart_data)

        # Assert
        assert response.status_code == 200
        houses = response.json()["houses"]

        assert len(houses) == 12  # Should have exactly 12 houses

        # Check structure of first house
        if len(houses) > 0:
            house = houses[0]
            assert "number" in house or "cusp_longitude" in house
            assert "sign" in house

    def test_quick_calculate_performance(self, client: TestClient, valid_chart_data):
        """Test that calculation completes in reasonable time"""
        import time

        # Act
        start_time = time.time()
        response = client.post("/api/charts/quick-calculate", json=valid_chart_data)
        end_time = time.time()

        # Assert
        assert response.status_code == 200
        duration = end_time - start_time
        assert duration < 5.0  # Should complete within 5 seconds

    def test_quick_calculate_multiple_requests(self, client: TestClient, valid_chart_data):
        """Test multiple sequential requests"""
        # Act & Assert - multiple requests should all succeed
        for i in range(3):
            valid_chart_data["name"] = f"Person {i}"
            response = client.post("/api/charts/quick-calculate", json=valid_chart_data)

            assert response.status_code == 200
            data = response.json()
            assert data["name"] == f"Person {i}"

    # Regression tests for bug fixes
    def test_boolean_checkboxes_not_strings(self, client: TestClient):
        """
        Regression test: Verify that boolean fields accept booleans, not strings.

        This test ensures the bug where checkbox values were sent as strings
        instead of booleans is fixed and won't return.
        """
        # Arrange - Use explicit boolean values
        data = {
            "name": "Regression Test",
            "birth_date": "1990-04-15",
            "birth_time": "14:30",
            "birth_city": "New York",
            "birth_country": "US",
            "birth_timezone": "America/New_York",
            "include_chiron": True,  # Must be boolean, not string "true"
            "include_lilith": False,  # Must be boolean, not string "false"
            "include_nodes": True,
        }

        # Act
        response = client.post("/api/charts/quick-calculate", json=data)

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert result["name"] == "Regression Test"

    def test_empty_coordinates_accepted_as_none(self, client: TestClient):
        """
        Regression test: Verify that omitted latitude/longitude work correctly.

        This test ensures the bug where empty coordinate fields sent NaN
        instead of undefined/null is fixed.
        """
        # Arrange - Omit latitude and longitude entirely
        data = {
            "name": "No Coordinates",
            "birth_date": "1990-04-15",
            "birth_time": "14:30",
            "birth_city": "New York",
            "birth_country": "US",
            "birth_timezone": "America/New_York",
            # No birth_latitude or birth_longitude
        }

        # Act
        response = client.post("/api/charts/quick-calculate", json=data)

        # Assert - Should succeed without coordinates
        assert response.status_code == 200
        result = response.json()
        assert result["name"] == "No Coordinates"

    def test_null_coordinates_accepted(self, client: TestClient):
        """
        Regression test: Verify that null latitude/longitude are handled correctly.

        This ensures the system properly handles null/None values for coordinates.
        """
        # Arrange - Explicitly set to null
        data = {
            "name": "Null Coordinates",
            "birth_date": "1990-04-15",
            "birth_time": "14:30",
            "birth_city": "Buenos Aires",
            "birth_country": "AR",
            "birth_timezone": "America/Argentina/Buenos_Aires",
            "birth_latitude": None,
            "birth_longitude": None,
        }

        # Act
        response = client.post("/api/charts/quick-calculate", json=data)

        # Assert - Should succeed with null coordinates
        assert response.status_code == 200
        result = response.json()
        assert result["name"] == "Null Coordinates"

    def test_valid_coordinates_as_floats(self, client: TestClient):
        """
        Regression test: Verify that valid float coordinates are accepted.

        This ensures the system correctly handles numeric coordinate values.
        """
        # Arrange
        data = {
            "name": "Valid Coordinates",
            "birth_date": "1985-12-25",
            "birth_time": "10:45",
            "birth_city": "Buenos Aires",
            "birth_country": "AR",
            "birth_timezone": "America/Argentina/Buenos_Aires",
            "birth_latitude": -34.6037,  # Must be float, not string
            "birth_longitude": -58.3816,  # Must be float, not string
        }

        # Act
        response = client.post("/api/charts/quick-calculate", json=data)

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert result["name"] == "Valid Coordinates"

    def test_checkbox_toggles_affect_planet_inclusion(self, client: TestClient):
        """
        Regression test: Verify that checkbox boolean values actually
        control planet inclusion in calculations.
        """
        # Arrange - Calculate with all bodies enabled
        data_with_all = {
            "name": "All Bodies",
            "birth_date": "1990-04-15",
            "birth_time": "14:30",
            "birth_city": "New York",
            "birth_country": "US",
            "birth_timezone": "America/New_York",
            "include_chiron": True,
            "include_lilith": True,
            "include_nodes": True,
        }

        # Arrange - Calculate with some bodies disabled
        data_without = {
            "name": "No Optional Bodies",
            "birth_date": "1990-04-15",
            "birth_time": "14:30",
            "birth_city": "New York",
            "birth_country": "US",
            "birth_timezone": "America/New_York",
            "include_chiron": False,
            "include_lilith": False,
            "include_nodes": False,
        }

        # Act
        response_with = client.post("/api/charts/quick-calculate", json=data_with_all)
        response_without = client.post("/api/charts/quick-calculate", json=data_without)

        # Assert
        assert response_with.status_code == 200
        assert response_without.status_code == 200

        planets_with = response_with.json()["planets"]
        planets_without = response_without.json()["planets"]

        # The chart with optional bodies should have more planets
        assert len(planets_with) > len(planets_without)
