"""
Unit Tests for QuickCalculateChartUseCase

Tests the quick chart calculation use case without database persistence.
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock

from src.application.use_cases.chart_calculation.quick_calculate_chart_use_case import (
    QuickCalculateChartUseCase
)
from src.application.dtos.quick_chart_dtos import QuickCalculateChartDTO
from src.domain.exceptions import CalculationError
from src.ports.calculators.astro_calculator import IAstrologicalCalculator


class TestQuickCalculateChartUseCase:
    """Test suite for QuickCalculateChartUseCase"""

    @pytest.fixture
    def mock_calculator(self):
        """Create a mock astrological calculator"""
        calculator = Mock(spec=IAstrologicalCalculator)

        # Mock successful natal chart calculation
        calculator.calculate_natal_chart.return_value = {
            "planets": [
                {
                    "name": "Sun",
                    "sign": "Aries",
                    "degree": 15.5,
                    "house": 1,
                    "is_retrograde": False
                },
                {
                    "name": "Moon",
                    "sign": "Taurus",
                    "degree": 23.8,
                    "house": 2,
                    "is_retrograde": False
                }
            ],
            "houses": [
                {"number": 1, "sign": "Aries", "degree": 0.0},
                {"number": 2, "sign": "Taurus", "degree": 30.0}
            ],
            "aspects": [
                {
                    "planet1": "Sun",
                    "planet2": "Moon",
                    "aspect_type": "sextile",
                    "orb": 1.7
                }
            ],
            "angles": {
                "ascendant": {"sign": "Aries", "degree": 0.0},
                "midheaven": {"sign": "Capricorn", "degree": 0.0}
            },
            "metadata": {
                "house_system": "placidus",
                "zodiac_type": "tropical"
            }
        }

        # Mock solar set calculation
        calculator.calculate_solar_set.return_value = {
            "sun_sign": "Aries",
            "sun_house": 1,
            "sun_degree": 15.5,
            "fifth_house_sign": "Leo",
            "hard_aspects": []
        }

        # Mock SVG generation
        calculator.generate_chart_svg.return_value = """<svg xmlns="http://www.w3.org/2000/svg">
            <circle cx="100" cy="100" r="50" />
        </svg>"""

        return calculator

    @pytest.fixture
    def use_case(self, mock_calculator):
        """Create use case instance with mocked dependencies"""
        return QuickCalculateChartUseCase(calculator=mock_calculator)

    @pytest.fixture
    def valid_dto(self):
        """Create a valid QuickCalculateChartDTO"""
        return QuickCalculateChartDTO(
            name="John Doe",
            birth_date="1990-04-15",
            birth_time="14:30",
            birth_city="New York",
            birth_country="US",
            birth_timezone="America/New_York",
            birth_latitude=40.7128,
            birth_longitude=-74.0060,
            include_chiron=True,
            include_lilith=True,
            include_nodes=True,
            house_system="placidus",
            language="en"
        )

    def test_execute_successful_calculation(self, use_case, valid_dto, mock_calculator):
        """Test successful chart calculation"""
        # Act
        result = use_case.execute(valid_dto)

        # Assert
        assert result is not None
        assert result.name == "John Doe"
        assert result.sun_sign == "Aries"
        assert len(result.planets) == 2
        assert len(result.houses) == 2
        assert len(result.aspects) == 1
        assert result.svg_data is not None
        assert "<svg" in result.svg_data
        assert result.house_system == "placidus"

        # Verify calculator was called correctly
        mock_calculator.calculate_natal_chart.assert_called_once()
        mock_calculator.calculate_solar_set.assert_called_once()
        mock_calculator.generate_chart_svg.assert_called_once()

    def test_execute_with_minimal_data(self, use_case, mock_calculator):
        """Test calculation with minimal required data (no coordinates)"""
        # Arrange
        dto = QuickCalculateChartDTO(
            name="Jane Smith",
            birth_date="1985-12-25",
            birth_time="08:00",
            birth_city="London",
            birth_country="GB",
            birth_timezone="Europe/London"
        )

        # Act
        result = use_case.execute(dto)

        # Assert
        assert result is not None
        assert result.name == "Jane Smith"
        mock_calculator.calculate_natal_chart.assert_called_once()

    def test_execute_with_invalid_date_format(self, use_case):
        """Test with invalid birth date format"""
        # Arrange
        dto = QuickCalculateChartDTO(
            name="Test",
            birth_date="15-04-1990",  # Wrong format
            birth_time="14:30",
            birth_city="New York",
            birth_country="US",
            birth_timezone="America/New_York"
        )

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            use_case.execute(dto)

        assert "Invalid birth date or time" in str(exc_info.value)

    def test_execute_with_invalid_time_format(self, use_case):
        """Test with invalid birth time format"""
        # Arrange
        dto = QuickCalculateChartDTO(
            name="Test",
            birth_date="1990-04-15",
            birth_time="2:30 PM",  # Wrong format
            birth_city="New York",
            birth_country="US",
            birth_timezone="America/New_York"
        )

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            use_case.execute(dto)

        assert "Invalid birth date or time" in str(exc_info.value)

    def test_execute_with_invalid_coordinates(self, use_case):
        """Test with invalid latitude/longitude values"""
        # Arrange
        dto = QuickCalculateChartDTO(
            name="Test",
            birth_date="1990-04-15",
            birth_time="14:30",
            birth_city="New York",
            birth_country="US",
            birth_timezone="America/New_York",
            birth_latitude=999.0,  # Invalid latitude
            birth_longitude=-74.0060
        )

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            use_case.execute(dto)

        assert "Invalid birth data" in str(exc_info.value)

    def test_execute_calculation_failure(self, use_case, valid_dto, mock_calculator):
        """Test handling of calculation failure"""
        # Arrange
        mock_calculator.calculate_natal_chart.side_effect = Exception("Calculation error")

        # Act & Assert
        with pytest.raises(CalculationError) as exc_info:
            use_case.execute(valid_dto)

        assert "Failed to calculate natal chart" in str(exc_info.value)

    def test_execute_solar_set_failure(self, use_case, valid_dto, mock_calculator):
        """Test handling of solar set calculation failure"""
        # Arrange
        mock_calculator.calculate_solar_set.side_effect = Exception("Solar set error")

        # Act & Assert
        with pytest.raises(CalculationError) as exc_info:
            use_case.execute(valid_dto)

        assert "Failed to calculate solar set" in str(exc_info.value)

    def test_execute_svg_generation_failure(self, use_case, valid_dto, mock_calculator):
        """Test handling of SVG generation failure"""
        # Arrange
        mock_calculator.generate_chart_svg.side_effect = Exception("SVG error")

        # Act & Assert
        with pytest.raises(CalculationError) as exc_info:
            use_case.execute(valid_dto)

        assert "Failed to generate SVG" in str(exc_info.value)

    def test_parse_birth_datetime_success(self, use_case):
        """Test successful datetime parsing"""
        # Act
        result = use_case._parse_birth_datetime("1990-04-15", "14:30")

        # Assert
        assert isinstance(result, datetime)
        assert result.year == 1990
        assert result.month == 4
        assert result.day == 15
        assert result.hour == 14
        assert result.minute == 30

    def test_parse_birth_datetime_edge_cases(self, use_case):
        """Test datetime parsing with edge case values"""
        # Test midnight
        result = use_case._parse_birth_datetime("2000-01-01", "00:00")
        assert result.hour == 0
        assert result.minute == 0

        # Test end of day
        result = use_case._parse_birth_datetime("2000-12-31", "23:59")
        assert result.hour == 23
        assert result.minute == 59

    def test_result_dto_to_dict(self, use_case, valid_dto):
        """Test conversion of result DTO to dictionary"""
        # Act
        result = use_case.execute(valid_dto)
        result_dict = result.to_dict()

        # Assert
        assert isinstance(result_dict, dict)
        assert result_dict["name"] == "John Doe"
        assert result_dict["sun_sign"] == "Aries"
        assert "planets" in result_dict
        assert "houses" in result_dict
        assert "aspects" in result_dict
        assert "svg_data" in result_dict
        assert "calculated_at" in result_dict

    def test_execute_with_different_house_systems(self, use_case, mock_calculator):
        """Test calculation with different house systems"""
        house_systems = ["placidus", "koch", "equal", "whole_sign"]

        for house_system in house_systems:
            dto = QuickCalculateChartDTO(
                name="Test",
                birth_date="1990-04-15",
                birth_time="14:30",
                birth_city="New York",
                birth_country="US",
                birth_timezone="America/New_York",
                house_system=house_system
            )

            # Act
            result = use_case.execute(dto)

            # Assert
            assert result.house_system == house_system

    def test_execute_with_different_languages(self, use_case, valid_dto):
        """Test calculation with different languages"""
        languages = ["en", "es", "it", "fr", "de", "pt"]

        for language in languages:
            valid_dto.language = language

            # Act
            result = use_case.execute(valid_dto)

            # Assert - should complete without error
            assert result is not None

    def test_execute_includes_optional_bodies(self, use_case, valid_dto, mock_calculator):
        """Test that optional celestial bodies are included when requested"""
        # Act
        result = use_case.execute(valid_dto)

        # Assert - verify calculator was called with correct flags
        call_args = mock_calculator.calculate_natal_chart.call_args
        assert call_args[1]["include_chiron"] is True
        assert call_args[1]["include_lilith"] is True
        assert call_args[1]["include_nodes"] is True

    def test_execute_excludes_optional_bodies(self, use_case, mock_calculator):
        """Test that optional celestial bodies can be excluded"""
        # Arrange
        dto = QuickCalculateChartDTO(
            name="Test",
            birth_date="1990-04-15",
            birth_time="14:30",
            birth_city="New York",
            birth_country="US",
            birth_timezone="America/New_York",
            include_chiron=False,
            include_lilith=False,
            include_nodes=False
        )

        # Act
        result = use_case.execute(dto)

        # Assert
        call_args = mock_calculator.calculate_natal_chart.call_args
        assert call_args[1]["include_chiron"] is False
        assert call_args[1]["include_lilith"] is False
        assert call_args[1]["include_nodes"] is False
