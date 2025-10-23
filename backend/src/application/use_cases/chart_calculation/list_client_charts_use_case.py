"""
List Client Charts Use Case

Retrieves all charts for a specific client.
"""
from uuid import UUID
from typing import List

from ...dtos.chart_dtos import NatalChartDTO
from ....domain.entities.user import User, UserRole
from ....domain.exceptions import ClientNotFoundError, UnauthorizedAccessError
from ....ports.repositories.client_repository import IClientRepository
from ....ports.repositories.chart_repository import INatalChartRepository


class ListClientChartsUseCase:
    """
    Use case for listing all charts for a client.

    Returns charts ordered by calculation date (newest first).
    """

    def __init__(
        self,
        client_repository: IClientRepository,
        chart_repository: INatalChartRepository
    ):
        self._client_repo = client_repository
        self._chart_repo = chart_repository

    def execute(
        self,
        client_id: str,
        current_user: User,
        skip: int = 0,
        limit: int = 100
    ) -> List[NatalChartDTO]:
        """
        Execute list client charts.

        Args:
            client_id: UUID of the client
            current_user: User requesting the charts
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of natal charts for the client

        Raises:
            ClientNotFoundError: If client doesn't exist
            UnauthorizedAccessError: If user cannot view this client's charts
        """
        # Get client to verify permissions
        client = self._client_repo.find_by_id(UUID(client_id))

        if not client:
            raise ClientNotFoundError(client_id)

        # Verify permissions
        if current_user.role != UserRole.ADMIN:
            if not client.belongs_to_consultant(current_user.id):
                raise UnauthorizedAccessError("You cannot view charts for this client")

        # Get charts
        charts = self._chart_repo.find_by_client(
            UUID(client_id),
            skip=skip,
            limit=limit
        )

        # Convert to DTOs
        return [NatalChartDTO.from_entity(chart) for chart in charts]
