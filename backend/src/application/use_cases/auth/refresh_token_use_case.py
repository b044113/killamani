"""
Refresh Token Use Case

Handles token refresh for authenticated users.
"""
from ...dtos.auth_dtos import RefreshTokenDTO, AuthTokensDTO
from ...services.token_service import TokenService
from ....domain.exceptions import InvalidCredentialsError, UserNotFoundError
from ....ports.repositories.user_repository import IUserRepository


class RefreshTokenUseCase:
    """
    Use case for refreshing authentication tokens.

    Validates refresh token and issues new access token.
    """

    def __init__(
        self,
        user_repository: IUserRepository,
        token_service: TokenService
    ):
        self._user_repo = user_repository
        self._token_service = token_service

    def execute(self, dto: RefreshTokenDTO) -> AuthTokensDTO:
        """
        Execute token refresh.

        Args:
            dto: Refresh token data

        Returns:
            New authentication tokens

        Raises:
            InvalidCredentialsError: If refresh token is invalid
            UserNotFoundError: If user no longer exists
        """
        # Verify refresh token
        user_id = self._token_service.verify_token(dto.refresh_token, token_type="refresh")

        # Verify user still exists and is active
        user = self._user_repo.find_by_id(user_id)

        if not user:
            raise UserNotFoundError(str(user_id))

        if not user.is_active:
            raise InvalidCredentialsError()

        # Generate new tokens
        access_token = self._token_service.create_access_token(
            user.id,
            additional_claims={"role": user.role.value}
        )
        refresh_token = self._token_service.create_refresh_token(user.id)

        return AuthTokensDTO(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=1800
        )
