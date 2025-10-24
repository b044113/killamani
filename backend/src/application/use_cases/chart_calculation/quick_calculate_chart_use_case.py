"""
Quick Calculate Chart Use Case

Handles quick calculation of natal charts without requiring client creation.
This supports the MVP requirement where any user can calculate a chart.
"""
from datetime import datetime
from typing import Optional

from ...dtos.quick_chart_dtos import QuickCalculateChartDTO, QuickChartResultDTO
from ....domain.value_objects.birth_data import BirthData
from ....domain.exceptions import CalculationError
from ....ports.calculators.astro_calculator import IAstrologicalCalculator


class QuickCalculateChartUseCase:
    """
    Use case for quick natal chart calculation.

    This use case allows any user (admin, consultant, or anonymous) to
    calculate a natal chart without creating a client entity first.

    Steps:
    1. Parse and validate birth data from DTO
    2. Create BirthData value object
    3. Calculate natal chart using calculator
    4. Calculate solar set
    5. Generate SVG export
    6. Return result DTO (without persisting to database)

    Note: This is a stateless operation - charts are not saved to the database.
    """

    def __init__(
        self,
        calculator: IAstrologicalCalculator,
    ):
        self._calculator = calculator

    def execute(
        self,
        dto: QuickCalculateChartDTO,
    ) -> QuickChartResultDTO:
        """
        Execute quick natal chart calculation.

        Args:
            dto: Calculation parameters with birth data

        Returns:
            Calculated natal chart with SVG

        Raises:
            CalculationError: If calculation or SVG generation fails
            ValueError: If birth data is invalid
        """
        # 1. Parse birth date and time
        try:
            birth_datetime = self._parse_birth_datetime(dto.birth_date, dto.birth_time)
        except ValueError as e:
            raise ValueError(f"Invalid birth date or time: {str(e)}")

        # 2. Create BirthData value object
        try:
            birth_data = BirthData(
                date=birth_datetime,
                city=dto.birth_city,
                country=dto.birth_country,
                timezone=dto.birth_timezone,
                latitude=dto.birth_latitude,
                longitude=dto.birth_longitude,
            )
        except ValueError as e:
            raise ValueError(f"Invalid birth data: {str(e)}")

        # 3. Calculate natal chart using calculator
        try:
            chart_data = self._calculator.calculate_natal_chart(
                birth_data=birth_data,
                include_chiron=dto.include_chiron,
                include_lilith=dto.include_lilith,
                include_nodes=dto.include_nodes,
            )
        except Exception as e:
            raise CalculationError(f"Failed to calculate natal chart: {str(e)}", "natal_chart")

        # 4. Calculate solar set
        try:
            solar_set = self._calculator.calculate_solar_set(chart_data)
        except Exception as e:
            raise CalculationError(f"Failed to calculate solar set: {str(e)}", "solar_set")

        # 5. Generate SVG export
        try:
            svg_data = self._calculator.generate_chart_svg(
                birth_data=birth_data,
                chart_data=chart_data,
                chart_name=dto.name,
                language=dto.language,
            )
        except Exception as e:
            raise CalculationError(f"Failed to generate SVG: {str(e)}", "svg_export")

        # 6. Create result DTO
        return QuickChartResultDTO(
            name=dto.name,
            sun_sign=solar_set.get("sun_sign", "Unknown"),
            planets=chart_data.get("planets", []),
            houses=chart_data.get("houses", []),
            aspects=chart_data.get("aspects", []),
            angles=chart_data.get("angles", {}),
            solar_set=solar_set,
            svg_data=svg_data,
            house_system=dto.house_system,
            calculated_at=datetime.utcnow(),
        )

    def _parse_birth_datetime(self, birth_date: str, birth_time: str) -> datetime:
        """
        Parse birth date and time strings into datetime object.

        Args:
            birth_date: Date in ISO format "YYYY-MM-DD"
            birth_time: Time in format "HH:MM"

        Returns:
            Combined datetime object

        Raises:
            ValueError: If date or time format is invalid
        """
        try:
            # Parse date (YYYY-MM-DD)
            date_parts = birth_date.split("-")
            if len(date_parts) != 3:
                raise ValueError("Date must be in YYYY-MM-DD format")

            year = int(date_parts[0])
            month = int(date_parts[1])
            day = int(date_parts[2])

            # Parse time (HH:MM)
            time_parts = birth_time.split(":")
            if len(time_parts) != 2:
                raise ValueError("Time must be in HH:MM format")

            hour = int(time_parts[0])
            minute = int(time_parts[1])

            # Create datetime
            return datetime(year, month, day, hour, minute)

        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid date/time format: {str(e)}")
