"""
Create Client Use Case

Handles creation of new clients by consultants.
"""
from ...dtos.client_dtos import CreateClientDTO, ClientDTO
from ....domain.entities.client import Client
from ....domain.entities.user import User
from ....domain.value_objects.birth_data import BirthData
from ....domain.exceptions import UnauthorizedAccessError, ValidationError
from ....ports.repositories.client_repository import IClientRepository
from ....ports.repositories.user_repository import IUserRepository


class CreateClientUseCase:
    """
    Use case for creating a new client.

    Only consultants and admins can create clients.
    """

    def __init__(
        self,
        client_repository: IClientRepository,
        user_repository: IUserRepository
    ):
        self._client_repo = client_repository
        self._user_repo = user_repository

    def execute(self, dto: CreateClientDTO, current_user: User) -> ClientDTO:
        """
        Execute client creation.

        Args:
            dto: Client creation data
            current_user: User performing the action

        Returns:
            Created client information

        Raises:
            UnauthorizedAccessError: If user cannot manage clients
            ValidationError: If client data is invalid
        """
        # Verify permissions
        if not current_user.can_manage_clients():
            raise UnauthorizedAccessError("Only consultants can create clients")

        # Create birth data value object
        try:
            birth_data = BirthData(
                date=dto.birth_data.date,
                city=dto.birth_data.city,
                country=dto.birth_data.country,
                timezone=dto.birth_data.timezone,
                latitude=dto.birth_data.latitude,
                longitude=dto.birth_data.longitude,
            )
        except ValueError as e:
            raise ValidationError(f"Invalid birth data: {str(e)}")

        # Create client entity
        client = Client(
            consultant_id=current_user.id,
            first_name=dto.first_name,
            last_name=dto.last_name,
            email=dto.email,
            birth_data=birth_data,
            notes=dto.notes or "",
        )

        # Save client
        saved_client = self._client_repo.save(client)

        return ClientDTO.from_entity(saved_client)
