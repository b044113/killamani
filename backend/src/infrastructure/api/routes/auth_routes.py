"""
Authentication API Routes

Endpoints for user authentication and registration.
"""
from fastapi import APIRouter, Depends, status

from ....application.dtos.auth_dtos import (
    LoginDTO,
    RegisterUserDTO,
    RefreshTokenDTO,
    AuthTokensDTO,
    UserDTO,
)
from ....application.use_cases.auth import (
    LoginUseCase,
    RegisterUserUseCase,
    RefreshTokenUseCase,
)
from ..dependencies.dependencies import (
    get_login_use_case,
    get_register_user_use_case,
    get_refresh_token_use_case,
)

router = APIRouter()


@router.post("/login", response_model=dict, status_code=status.HTTP_200_OK)
async def login(
    credentials: LoginDTO,
    use_case: LoginUseCase = Depends(get_login_use_case)
):
    """
    Login with email and password.

    Returns authentication tokens and user information.
    """
    tokens, user = use_case.execute(credentials)

    return {
        "access_token": tokens.access_token,
        "refresh_token": tokens.refresh_token,
        "token_type": tokens.token_type,
        "expires_in": tokens.expires_in,
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "preferred_language": user.preferred_language,
        }
    }


@router.post("/register", response_model=UserDTO, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: RegisterUserDTO,
    use_case: RegisterUserUseCase = Depends(get_register_user_use_case)
):
    """
    Register a new user account.

    Returns created user information.
    """
    return use_case.execute(user_data)


@router.post("/refresh", response_model=AuthTokensDTO, status_code=status.HTTP_200_OK)
async def refresh_token(
    refresh_data: RefreshTokenDTO,
    use_case: RefreshTokenUseCase = Depends(get_refresh_token_use_case)
):
    """
    Refresh access token using refresh token.

    Returns new authentication tokens.
    """
    return use_case.execute(refresh_data)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout():
    """
    Logout user.

    Client should discard tokens after calling this endpoint.
    """
    # In a stateless JWT setup, logout is handled client-side
    # In production, you might want to implement token blacklisting
    return None
