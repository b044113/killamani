"""
Calculate Natal Chart Use Case

Handles calculation of natal (birth) charts.
"""
from uuid import UUID

from ...dtos.chart_dtos import CalculateNatalChartDTO, NatalChartDTO
from ....domain.entities.natal_chart import NatalChart
from ....domain.entities.user import User, UserRole
from ....domain.exceptions import (
    ClientNotFoundError,
    UnauthorizedAccessError,
    CalculationError
)
from ....ports.repositories.client_repository import IClientRepository
from ....ports.repositories.chart_repository import INatalChartRepository
from ....ports.calculators.astro_calculator import IAstrologicalCalculator
from ....ports.interpreters.chart_interpreter import IChartInterpreter


class CalculateNatalChartUseCase:
    """
    Use case for calculating natal charts.

    Steps:
    1. Validate user permissions
    2. Get client and birth data
    3. Calculate natal chart using calculator
    4. Calculate solar set
    5. Generate interpretations
    6. Save chart to repository
    7. Return chart DTO
    """

    def __init__(
        self,
        client_repository: IClientRepository,
        chart_repository: INatalChartRepository,
        calculator: IAstrologicalCalculator,
        interpreter: IChartInterpreter
    ):
        self._client_repo = client_repository
        self._chart_repo = chart_repository
        self._calculator = calculator
        self._interpreter = interpreter

    def execute(
        self,
        dto: CalculateNatalChartDTO,
        current_user: User
    ) -> NatalChartDTO:
        """
        Execute natal chart calculation.

        Args:
            dto: Calculation parameters
            current_user: User requesting the calculation

        Returns:
            Calculated natal chart

        Raises:
            ClientNotFoundError: If client doesn't exist
            UnauthorizedAccessError: If user cannot access this client
            CalculationError: If calculation fails
        """
        # 1. Get client and validate permissions
        client = self._client_repo.find_by_id(UUID(dto.client_id))

        if not client:
            raise ClientNotFoundError(dto.client_id)

        if current_user.role != UserRole.ADMIN:
            if not client.belongs_to_consultant(current_user.id):
                raise UnauthorizedAccessError("You cannot calculate charts for this client")

        # 2. Calculate natal chart using calculator
        try:
            chart_data = self._calculator.calculate_natal_chart(
                birth_data=client.birth_data,
                include_chiron=dto.include_chiron,
                include_lilith=dto.include_lilith,
                include_nodes=dto.include_nodes,
            )
        except Exception as e:
            raise CalculationError(f"Failed to calculate natal chart: {str(e)}", "natal_chart")

        # 3. Calculate solar set
        try:
            solar_set = self._calculator.calculate_solar_set(chart_data)
        except Exception as e:
            raise CalculationError(f"Failed to calculate solar set: {str(e)}", "solar_set")

        # 4. Generate interpretations
        try:
            # Create a temporary chart entity for interpretation
            temp_chart = NatalChart(
                client_id=client.id,
                data=chart_data,
                solar_set=solar_set,
                house_system=dto.house_system,
            )

            interpretations = self._interpreter.interpret_natal_chart(
                chart=temp_chart,
                language=dto.language,
                detail_level="standard"
            )
        except Exception as e:
            # If interpretation fails, continue with empty interpretations
            interpretations = {dto.language: {}}

        # 5. Create chart entity
        chart = NatalChart(
            client_id=client.id,
            data=chart_data,
            solar_set=solar_set,
            house_system=dto.house_system,
            interpretations={dto.language: interpretations},
        )

        # 6. Save chart
        saved_chart = self._chart_repo.save(chart)

        # 7. Return DTO
        return NatalChartDTO.from_entity(saved_chart)
