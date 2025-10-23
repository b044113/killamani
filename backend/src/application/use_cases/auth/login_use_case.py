"""
Login Use Case

Handles user authentication.
"""
from ...dtos.auth_dtos import LoginDTO, AuthTokensDTO, UserDTO
from ...services.password_service import PasswordService
from ...services.token_service import TokenService
from ....domain.exceptions import InvalidCredentialsError
from ....ports.repositories.user_repository import IUserRepository


class LoginUseCase:
    """
    Use case for user login.

    Validates credentials and returns authentication tokens.
    """

    def __init__(
        self,
        user_repository: IUserRepository,
        password_service: PasswordService,
        token_service: TokenService
    ):
        self._user_repo = user_repository
        self._password_service = password_service
        self._token_service = token_service

    def execute(self, dto: LoginDTO) -> tuple[AuthTokensDTO, UserDTO]:
        """
        Execute login use case.

        Args:
            dto: Login credentials

        Returns:
            Tuple of (tokens, user_info)

        Raises:
            InvalidCredentialsError: If email or password is incorrect
        """
        # Find user by email
        user = self._user_repo.find_by_email(dto.email)

        if not user:
            raise InvalidCredentialsError()

        # Verify password
        if not self._password_service.verify_password(dto.password, user.hashed_password):
            raise InvalidCredentialsError()

        # Check if user is active
        if not user.is_active:
            raise InvalidCredentialsError()

        # Generate tokens
        access_token = self._token_service.create_access_token(
            user.id,
            additional_claims={"role": user.role.value}
        )
        refresh_token = self._token_service.create_refresh_token(user.id)

        tokens = AuthTokensDTO(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=1800  # 30 minutes
        )

        user_dto = UserDTO.from_entity(user)

        return tokens, user_dto
