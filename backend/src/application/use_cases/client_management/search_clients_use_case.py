"""
Search Clients Use Case

Handles searching for clients by name or email.
"""
from ...dtos.client_dtos import SearchClientsDTO, ClientDTO, ClientListDTO
from ....domain.entities.user import User, UserRole
from ....domain.exceptions import UnauthorizedAccessError
from ....ports.repositories.client_repository import IClientRepository


class SearchClientsUseCase:
    """
    Use case for searching clients.

    Consultants search only their clients, admins search all.
    """

    def __init__(self, client_repository: IClientRepository):
        self._client_repo = client_repository

    def execute(self, dto: SearchClientsDTO, current_user: User) -> ClientListDTO:
        """
        Execute client search.

        Args:
            dto: Search parameters
            current_user: User performing the search

        Returns:
            List of matching clients

        Raises:
            UnauthorizedAccessError: If user cannot search clients
        """
        # Verify permissions
        if not current_user.can_manage_clients():
            raise UnauthorizedAccessError("Only consultants can search clients")

        # Search clients based on role
        if current_user.role == UserRole.ADMIN:
            # Admins search all clients
            clients = self._client_repo.search(
                query=dto.query,
                skip=dto.skip,
                limit=dto.limit
            )
        else:
            # Consultants search only their clients
            clients = self._client_repo.search(
                query=dto.query,
                consultant_id=current_user.id,
                skip=dto.skip,
                limit=dto.limit
            )

        # Convert to DTOs
        client_dtos = [ClientDTO.from_entity(client) for client in clients]

        return ClientListDTO(
            clients=client_dtos,
            total=len(client_dtos),
            skip=dto.skip,
            limit=dto.limit
        )
