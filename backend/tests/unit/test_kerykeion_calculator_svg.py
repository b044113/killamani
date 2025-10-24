"""
Unit Tests for KerykeionCalculator SVG Generation

Tests the SVG generation methods in KerykeionCalculator.
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.adapters.calculators.kerykeion_calculator import KerykeionCalculator
from src.domain.value_objects.birth_data import BirthData
from src.domain.exceptions import CalculationError


class TestKerykeionCalculatorSVG:
    """Test suite for SVG generation in KerykeionCalculator"""

    @pytest.fixture
    def calculator(self):
        """Create calculator instance"""
        return KerykeionCalculator()

    @pytest.fixture
    def sample_birth_data(self):
        """Create sample birth data"""
        return BirthData(
            date=datetime(1990, 4, 15, 14, 30),
            city="New York",
            country="US",
            timezone="America/New_York",
            latitude=40.7128,
            longitude=-74.0060
        )

    @pytest.fixture
    def sample_chart_data(self):
        """Create sample chart data"""
        return {
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
            }
        }

    def test_generate_basic_svg_structure(self, calculator, sample_chart_data):
        """Test basic SVG generation structure"""
        # Act
        svg = calculator._generate_basic_svg(sample_chart_data, "Test Chart")

        # Assert
        assert svg is not None
        assert isinstance(svg, str)
        assert svg.startswith('<?xml version="1.0"')
        assert '<svg' in svg
        assert '</svg>' in svg
        assert 'xmlns="http://www.w3.org/2000/svg"' in svg

    def test_generate_basic_svg_contains_title(self, calculator, sample_chart_data):
        """Test that SVG contains chart title"""
        # Act
        svg = calculator._generate_basic_svg(sample_chart_data, "My Natal Chart")

        # Assert
        assert "My Natal Chart" in svg
        assert "Natal Chart" in svg  # Subtitle

    def test_generate_basic_svg_contains_planets(self, calculator, sample_chart_data):
        """Test that SVG contains planet information"""
        # Act
        svg = calculator._generate_basic_svg(sample_chart_data, "Test")

        # Assert
        assert "Sun" in svg
        assert "Moon" in svg
        assert "Aries" in svg
        assert "Taurus" in svg

    def test_generate_basic_svg_contains_ascendant(self, calculator, sample_chart_data):
        """Test that SVG contains ascendant information"""
        # Act
        svg = calculator._generate_basic_svg(sample_chart_data, "Test")

        # Assert
        assert "Ascendant" in svg

    def test_generate_basic_svg_retrograde_symbol(self, calculator):
        """Test retrograde planet symbol in SVG"""
        # Arrange
        chart_data = {
            "planets": [
                {
                    "name": "Mercury",
                    "sign": "Gemini",
                    "degree": 10.0,
                    "house": 3,
                    "is_retrograde": True
                }
            ],
            "houses": [],
            "aspects": [],
            "angles": {}
        }

        # Act
        svg = calculator._generate_basic_svg(chart_data, "Test")

        # Assert
        assert "Mercury" in svg
        assert "℞" in svg  # Retrograde symbol

    def test_generate_basic_svg_with_empty_chart_data(self, calculator):
        """Test SVG generation with empty chart data"""
        # Arrange
        empty_chart = {
            "planets": [],
            "houses": [],
            "aspects": [],
            "angles": {}
        }

        # Act
        svg = calculator._generate_basic_svg(empty_chart, "Empty Chart")

        # Assert
        assert svg is not None
        assert '<svg' in svg
        assert "Empty Chart" in svg

    def test_generate_basic_svg_with_many_planets(self, calculator):
        """Test SVG generation with many planets"""
        # Arrange
        chart_data = {
            "planets": [
                {"name": f"Planet{i}", "sign": "Aries", "degree": float(i),
                 "house": i % 12 + 1, "is_retrograde": False}
                for i in range(15)
            ],
            "houses": [],
            "aspects": [],
            "angles": {}
        }

        # Act
        svg = calculator._generate_basic_svg(chart_data, "Test")

        # Assert
        # Should only show first 10 planets
        assert "Planet0" in svg
        assert "Planet9" in svg

    @patch('src.adapters.calculators.kerykeion_calculator.KerykeionChartSVG')
    @patch('src.adapters.calculators.kerykeion_calculator.AstrologicalSubject')
    def test_generate_chart_svg_success(
        self,
        mock_subject_class,
        mock_svg_class,
        calculator,
        sample_birth_data,
        sample_chart_data
    ):
        """Test successful SVG generation using Kerykeion"""
        # Arrange
        mock_subject = MagicMock()
        mock_subject_class.return_value = mock_subject

        mock_chart_svg = MagicMock()
        mock_chart_svg.makeSVG.return_value = "<svg>Chart SVG</svg>"
        mock_svg_class.return_value = mock_chart_svg

        # Act
        svg = calculator.generate_chart_svg(
            birth_data=sample_birth_data,
            chart_data=sample_chart_data,
            chart_name="Test Chart",
            language="en"
        )

        # Assert
        assert svg == "<svg>Chart SVG</svg>"
        mock_subject_class.assert_called_once()
        mock_svg_class.assert_called_once()

    @patch('src.adapters.calculators.kerykeion_calculator.AstrologicalSubject')
    def test_generate_chart_svg_fallback_on_error(
        self,
        mock_subject_class,
        calculator,
        sample_birth_data,
        sample_chart_data
    ):
        """Test fallback to basic SVG when Kerykeion fails"""
        # Arrange
        mock_subject_class.side_effect = Exception("Kerykeion error")

        # Act
        svg = calculator.generate_chart_svg(
            birth_data=sample_birth_data,
            chart_data=sample_chart_data,
            chart_name="Test Chart",
            language="en"
        )

        # Assert - should return basic SVG
        assert svg is not None
        assert '<svg' in svg
        assert "Test Chart" in svg

    def test_generate_chart_svg_different_languages(
        self,
        calculator,
        sample_birth_data,
        sample_chart_data
    ):
        """Test SVG generation with different languages"""
        languages = ["en", "es", "it", "fr", "de", "pt"]

        for language in languages:
            # Act
            svg = calculator.generate_chart_svg(
                birth_data=sample_birth_data,
                chart_data=sample_chart_data,
                chart_name="Test",
                language=language
            )

            # Assert - should not raise error
            assert svg is not None

    def test_export_chart_svg_creates_file(self, calculator, sample_chart_data, tmp_path):
        """Test that export_chart_svg creates an SVG file"""
        # Act
        file_path = calculator.export_chart_svg(
            chart_data=sample_chart_data,
            output_path=str(tmp_path),
            language="en"
        )

        # Assert
        assert file_path is not None
        assert file_path.endswith('.svg')

    def test_svg_contains_valid_xml(self, calculator, sample_chart_data):
        """Test that generated SVG is valid XML"""
        # Act
        svg = calculator._generate_basic_svg(sample_chart_data, "Test")

        # Assert - basic XML validation
        assert svg.count('<svg') == svg.count('</svg>')
        assert svg.count('<circle') == svg.count('/>')  # Self-closing or closed tags

    def test_svg_viewbox_dimensions(self, calculator, sample_chart_data):
        """Test that SVG has proper viewBox dimensions"""
        # Act
        svg = calculator._generate_basic_svg(sample_chart_data, "Test")

        # Assert
        assert 'viewBox="0 0 800 900"' in svg
        assert 'width="800"' in svg
        assert 'height="900"' in svg

    def test_svg_styling(self, calculator, sample_chart_data):
        """Test that SVG contains CSS styling"""
        # Act
        svg = calculator._generate_basic_svg(sample_chart_data, "Test")

        # Assert
        assert '<style>' in svg
        assert '.title' in svg
        assert '.planet' in svg
        assert '.circle' in svg
        assert '.zodiac' in svg
