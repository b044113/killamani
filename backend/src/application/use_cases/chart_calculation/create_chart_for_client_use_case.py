"""
Create Chart For Client Use Case

Handles creation of natal charts for existing clients.
"""
from datetime import datetime
from uuid import UUID

from ...dtos.chart_dtos import CreateChartForClientDTO, NatalChartDTO
from ....domain.entities.natal_chart import NatalChart
from ....domain.entities.user import User, UserRole
from ....domain.value_objects.birth_data import BirthData
from ....domain.exceptions import (
    ClientNotFoundError,
    UnauthorizedAccessError,
    CalculationError
)
from ....ports.calculators.astro_calculator import IAstrologicalCalculator
from ....ports.repositories.client_repository import IClientRepository
from ....ports.repositories.chart_repository import INatalChartRepository


class CreateChartForClientUseCase:
    """
    Use case for creating a natal chart for an existing client.

    This allows adding multiple charts to a single client (e.g., birth chart,
    rectified chart, etc.).

    Steps:
    1. Verify client exists and user has permission
    2. Parse and validate birth data from DTO
    3. Create BirthData value object
    4. Calculate natal chart using calculator
    5. Calculate solar set
    6. Generate SVG export
    7. Create NatalChart entity
    8. Save to repository
    9. Return NatalChartDTO
    """

    def __init__(
        self,
        calculator: IAstrologicalCalculator,
        client_repository: IClientRepository,
        chart_repository: INatalChartRepository,
    ):
        self._calculator = calculator
        self._client_repo = client_repository
        self._chart_repo = chart_repository

    def execute(
        self,
        client_id: str,
        dto: CreateChartForClientDTO,
        current_user: User,
    ) -> NatalChartDTO:
        """
        Execute natal chart creation for client.

        Args:
            client_id: ID of the client to create chart for
            dto: Chart creation parameters with birth data
            current_user: User performing the action

        Returns:
            Created natal chart with SVG

        Raises:
            ClientNotFoundError: If client doesn't exist
            UnauthorizedAccessError: If user cannot add charts to this client
            CalculationError: If calculation or SVG generation fails
            ValueError: If birth data is invalid
        """
        # 1. Verify client exists and user has permission
        client = self._client_repo.find_by_id(UUID(client_id))
        if not client:
            raise ClientNotFoundError(client_id)

        # Check permissions (consultants can only add charts to their clients)
        if current_user.role != UserRole.ADMIN:
            if not client.belongs_to_consultant(current_user.id):
                raise UnauthorizedAccessError("You cannot add charts to this client")

        # 2. Parse birth date and time
        try:
            birth_datetime = self._parse_birth_datetime(dto.birth_date, dto.birth_time)
        except ValueError as e:
            raise ValueError(f"Invalid birth date or time: {str(e)}")

        # 3. Create BirthData value object
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

        # 4. Calculate natal chart using calculator
        try:
            chart_data = self._calculator.calculate_natal_chart(
                birth_data=birth_data,
                include_chiron=dto.include_chiron,
                include_lilith=dto.include_lilith,
                include_nodes=dto.include_nodes,
            )
        except Exception as e:
            raise CalculationError(f"Failed to calculate natal chart: {str(e)}", "natal_chart")

        # 5. Calculate solar set
        try:
            solar_set = self._calculator.calculate_solar_set(chart_data)
        except Exception as e:
            raise CalculationError(f"Failed to calculate solar set: {str(e)}", "solar_set")

        # 6. Generate SVG export
        try:
            svg_data = self._calculator.generate_chart_svg(
                birth_data=birth_data,
                chart_data=chart_data,
                chart_name=dto.name,
                language=dto.language,
            )
        except Exception as e:
            raise CalculationError(f"Failed to generate SVG: {str(e)}", "svg_export")

        # 7. Create NatalChart entity
        natal_chart = NatalChart(
            client_id=client.id,
            name=dto.name,
            data=chart_data,
            solar_set=solar_set,
            house_system=dto.house_system,
            calculated_at=datetime.utcnow(),
        )

        # Store SVG data (for now, we'll store it as svg_url, but this could be improved)
        # TODO: Save SVG to file storage and set URL
        natal_chart.svg_url = f"data:image/svg+xml;base64,{svg_data}"

        # 8. Save to repository
        saved_chart = self._chart_repo.save(natal_chart)

        # 9. Return DTO
        return NatalChartDTO.from_entity(saved_chart)

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
