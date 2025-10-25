"""
Update Client Use Case

Handles updating client information.
"""
from uuid import UUID

from ...dtos.client_dtos import UpdateClientDTO, ClientDTO
from ....domain.entities.user import User, UserRole
from ....domain.exceptions import ClientNotFoundError, UnauthorizedAccessError
from ....ports.repositories.client_repository import IClientRepository


class UpdateClientUseCase:
    """
    Use case for updating client information.

    Consultants can only update their own clients, admins can update all.
    """

    def __init__(self, client_repository: IClientRepository):
        self._client_repo = client_repository

    def execute(self, dto: UpdateClientDTO, current_user: User) -> ClientDTO:
        """
        Execute client update.

        Args:
            dto: Update data
            current_user: User performing the update

        Returns:
            Updated client information

        Raises:
            ClientNotFoundError: If client doesn't exist
            UnauthorizedAccessError: If user cannot update this client
        """
        # Find client
        client = self._client_repo.find_by_id(UUID(dto.client_id))

        if not client:
            raise ClientNotFoundError(dto.client_id)

        # Verify permissions
        if current_user.role != UserRole.ADMIN:
            if not client.belongs_to_consultant(current_user.id):
                raise UnauthorizedAccessError("You cannot update this client")

        # Update fields (only if provided)
        if dto.first_name is not None:
            client.first_name = dto.first_name

        if dto.last_name is not None:
            client.last_name = dto.last_name

        if dto.email is not None or dto.phone is not None:
            client.update_contact_info(email=dto.email, phone=dto.phone)

        if dto.notes is not None:
            client.update_notes(dto.notes)

        # Save updated client
        updated_client = self._client_repo.save(client)

        return ClientDTO.from_entity(updated_client)
