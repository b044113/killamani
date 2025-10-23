"""
Register User Use Case

Handles new user registration.
"""
from ...dtos.auth_dtos import RegisterUserDTO, UserDTO
from ...services.password_service import PasswordService
from ....domain.entities.user import User
from ....domain.exceptions import DuplicateEntityError
from ....ports.repositories.user_repository import IUserRepository


class RegisterUserUseCase:
    """
    Use case for user registration.

    Creates a new user account.
    """

    def __init__(
        self,
        user_repository: IUserRepository,
        password_service: PasswordService
    ):
        self._user_repo = user_repository
        self._password_service = password_service

    def execute(self, dto: RegisterUserDTO) -> UserDTO:
        """
        Execute user registration.

        Args:
            dto: Registration data

        Returns:
            Created user information

        Raises:
            DuplicateEntityError: If email already exists
        """
        # Check if email already exists
        if self._user_repo.exists_by_email(dto.email):
            raise DuplicateEntityError("User", "email", dto.email)

        # Hash password
        hashed_password = self._password_service.hash_password(dto.password)

        # Create user entity
        user = User(
            email=dto.email,
            hashed_password=hashed_password,
            role=dto.role,
            preferred_language=dto.preferred_language,
        )

        # Save user
        saved_user = self._user_repo.save(user)

        return UserDTO.from_entity(saved_user)
