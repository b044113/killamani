"""
Get Client Details Use Case

Retrieves detailed information about a specific client.
"""
from uuid import UUID

from ...dtos.client_dtos import ClientDTO
from ....domain.entities.user import User, UserRole
from ....domain.exceptions import ClientNotFoundError, UnauthorizedAccessError
from ....ports.repositories.client_repository import IClientRepository


class GetClientDetailsUseCase:
    """
    Use case for retrieving client details.

    Consultants can only view their own clients, admins can view all.
    """

    def __init__(self, client_repository: IClientRepository):
        self._client_repo = client_repository

    def execute(self, client_id: str, current_user: User) -> ClientDTO:
        """
        Execute get client details.

        Args:
            client_id: UUID of the client to retrieve
            current_user: User requesting the details

        Returns:
            Client details

        Raises:
            ClientNotFoundError: If client doesn't exist
            UnauthorizedAccessError: If user cannot view this client
        """
        # Find client
        client = self._client_repo.find_by_id(UUID(client_id))

        if not client:
            raise ClientNotFoundError(client_id)

        # Verify permissions
        if current_user.role != UserRole.ADMIN:
            # Non-admin users can only view their own clients
            if not client.belongs_to_consultant(current_user.id):
                raise UnauthorizedAccessError("You cannot view this client")

        return ClientDTO.from_entity(client)
