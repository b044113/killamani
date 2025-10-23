"""
Token Service

Handles JWT token generation and validation.
"""
from datetime import datetime, timedelta
from typing import Dict, Optional
from uuid import UUID

from jose import JWTError, jwt

from ...infrastructure.config.settings import get_settings
from ...domain.exceptions import InvalidCredentialsError

settings = get_settings()


class TokenService:
    """Service for JWT token management."""

    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_minutes = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS

    def create_access_token(self, user_id: UUID, additional_claims: Optional[Dict] = None) -> str:
        """
        Create JWT access token.

        Args:
            user_id: User's UUID
            additional_claims: Additional data to include in token

        Returns:
            JWT access token
        """
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        to_encode = {
            "sub": str(user_id),
            "exp": expire,
            "type": "access"
        }

        if additional_claims:
            to_encode.update(additional_claims)

        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, user_id: UUID) -> str:
        """
        Create JWT refresh token.

        Args:
            user_id: User's UUID

        Returns:
            JWT refresh token
        """
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)

        to_encode = {
            "sub": str(user_id),
            "exp": expire,
            "type": "refresh"
        }

        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str, token_type: str = "access") -> UUID:
        """
        Verify and decode JWT token.

        Args:
            token: JWT token to verify
            token_type: Expected token type (access or refresh)

        Returns:
            User ID from token

        Raises:
            InvalidCredentialsError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Verify token type
            if payload.get("type") != token_type:
                raise InvalidCredentialsError()

            # Extract user ID
            user_id_str = payload.get("sub")
            if not user_id_str:
                raise InvalidCredentialsError()

            return UUID(user_id_str)

        except JWTError:
            raise InvalidCredentialsError()

    def decode_token(self, token: str) -> Dict:
        """
        Decode token without verification (for debugging).

        Args:
            token: JWT token

        Returns:
            Token payload
        """
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except JWTError:
            raise InvalidCredentialsError()
