"""
Get Chart Details Use Case

Retrieves a previously calculated natal chart.
"""
from uuid import UUID

from ...dtos.chart_dtos import NatalChartDTO
from ....domain.entities.user import User, UserRole
from ....domain.exceptions import (
    ChartNotFoundError,
    UnauthorizedAccessError,
    ClientNotFoundError
)
from ....ports.repositories.client_repository import IClientRepository
from ....ports.repositories.chart_repository import INatalChartRepository


class GetChartDetailsUseCase:
    """
    Use case for retrieving natal chart details.

    Validates user permissions before returning chart.
    """

    def __init__(
        self,
        client_repository: IClientRepository,
        chart_repository: INatalChartRepository
    ):
        self._client_repo = client_repository
        self._chart_repo = chart_repository

    def execute(self, chart_id: str, current_user: User) -> NatalChartDTO:
        """
        Execute get chart details.

        Args:
            chart_id: UUID of the chart to retrieve
            current_user: User requesting the chart

        Returns:
            Natal chart details

        Raises:
            ChartNotFoundError: If chart doesn't exist
            UnauthorizedAccessError: If user cannot view this chart
        """
        # Find chart
        chart = self._chart_repo.find_by_id(UUID(chart_id))

        if not chart:
            raise ChartNotFoundError(chart_id)

        # Get client to verify permissions
        client = self._client_repo.find_by_id(chart.client_id)

        if not client:
            raise ClientNotFoundError(str(chart.client_id))

        # Verify permissions
        if current_user.role != UserRole.ADMIN:
            if not client.belongs_to_consultant(current_user.id):
                raise UnauthorizedAccessError("You cannot view this chart")

        return NatalChartDTO.from_entity(chart)
