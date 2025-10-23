"""
List Clients Use Case

Retrieves list of clients for a consultant.
"""
from ...dtos.client_dtos import ClientDTO, ClientListDTO
from ....domain.entities.user import User, UserRole
from ....domain.exceptions import UnauthorizedAccessError
from ....ports.repositories.client_repository import IClientRepository


class ListClientsUseCase:
    """
    Use case for listing clients.

    Consultants see only their clients, admins see all.
    """

    def __init__(self, client_repository: IClientRepository):
        self._client_repo = client_repository

    def execute(
        self,
        current_user: User,
        skip: int = 0,
        limit: int = 100
    ) -> ClientListDTO:
        """
        Execute list clients.

        Args:
            current_user: User requesting the list
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return

        Returns:
            List of clients with pagination info

        Raises:
            UnauthorizedAccessError: If user cannot view clients
        """
        # Verify permissions
        if not current_user.can_manage_clients():
            raise UnauthorizedAccessError("Only consultants can view clients")

        # Get clients based on role
        if current_user.role == UserRole.ADMIN:
            # Admins see all clients
            clients = self._client_repo.find_all(skip=skip, limit=limit)
            # For total, we'd need a count method - for now, approximate
            total = len(clients)
        else:
            # Consultants see only their clients
            clients = self._client_repo.find_by_consultant(
                current_user.id,
                skip=skip,
                limit=limit
            )
            total = self._client_repo.count_by_consultant(current_user.id)

        # Convert to DTOs
        client_dtos = [ClientDTO.from_entity(client) for client in clients]

        return ClientListDTO(
            clients=client_dtos,
            total=total,
            skip=skip,
            limit=limit
        )
