"""
Unit tests for TokenService
"""
import pytest
from datetime import datetime, timedelta, timezone
from uuid import UUID
from jose import jwt
from src.application.services.token_service import TokenService
from src.domain.entities.user import UserRole
from src.domain.exceptions import InvalidCredentialsError


@pytest.mark.unit
class TestTokenService:
    """Test JWT token generation and validation"""

    def test_create_access_token(self, token_service: TokenService):
        """Test creating access token"""
        user_id = UUID("12345678-1234-1234-1234-123456789012")
        role = UserRole.CONSULTANT

        token = token_service.create_access_token(
            user_id,
            additional_claims={"role": role.value}
        )

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self, token_service: TokenService):
        """Test creating refresh token"""
        user_id = UUID("12345678-1234-1234-1234-123456789012")

        token = token_service.create_refresh_token(user_id)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_access_token_valid(self, token_service: TokenService):
        """Test verifying valid access token"""
        user_id = UUID("12345678-1234-1234-1234-123456789012")
        role = UserRole.ADMIN

        token = token_service.create_access_token(
            user_id,
            additional_claims={"role": role.value}
        )

        result_user_id = token_service.verify_token(token, token_type="access")

        assert result_user_id is not None
        assert isinstance(result_user_id, UUID)
        assert result_user_id == user_id

    def test_verify_refresh_token_valid(self, token_service: TokenService):
        """Test verifying valid refresh token"""
        user_id = UUID("12345678-1234-1234-1234-123456789012")
        token = token_service.create_refresh_token(user_id)

        result_user_id = token_service.verify_token(token, token_type="refresh")

        assert result_user_id is not None
        assert isinstance(result_user_id, UUID)
        assert result_user_id == user_id

    def test_verify_token_expired(self, token_service: TokenService):
        """Test verifying expired token raises error"""
        user_id = UUID("12345678-1234-1234-1234-123456789012")

        # Create token with negative expiration (already expired)
        payload = {
            "sub": str(user_id),
            "exp": datetime.utcnow() - timedelta(minutes=1),
            "type": "access",
            "role": "user"
        }
        expired_token = jwt.encode(payload, token_service.secret_key, algorithm=token_service.algorithm)

        with pytest.raises(InvalidCredentialsError):
            token_service.verify_token(expired_token)

    def test_verify_token_invalid_signature(self, token_service: TokenService):
        """Test verifying token with invalid signature raises error"""
        user_id = UUID("12345678-1234-1234-1234-123456789012")

        # Create token with different secret
        payload = {
            "sub": str(user_id),
            "exp": datetime.utcnow() + timedelta(minutes=30),
            "type": "access",
            "role": "user"
        }
        invalid_token = jwt.encode(payload, "wrong-secret-key", algorithm="HS256")

        with pytest.raises(InvalidCredentialsError):
            token_service.verify_token(invalid_token)

    def test_verify_token_malformed(self, token_service: TokenService):
        """Test verifying malformed token raises error"""
        malformed_token = "not.a.valid.jwt.token"

        with pytest.raises(InvalidCredentialsError):
            token_service.verify_token(malformed_token)

    def test_verify_token_wrong_type(self, token_service: TokenService):
        """Test verifying token with wrong type raises error"""
        user_id = UUID("12345678-1234-1234-1234-123456789012")

        # Create refresh token
        refresh_token = token_service.create_refresh_token(user_id)

        # Try to verify as access token
        with pytest.raises(InvalidCredentialsError):
            token_service.verify_token(refresh_token, token_type="access")

    def test_decode_token_with_role(self, token_service: TokenService):
        """Test that access token can be decoded and contains role"""
        user_id = UUID("12345678-1234-1234-1234-123456789012")
        role = UserRole.CONSULTANT

        token = token_service.create_access_token(
            user_id,
            additional_claims={"role": role.value}
        )

        payload = token_service.decode_token(token)

        assert "role" in payload
        assert payload["role"] == role.value
        assert payload["type"] == "access"
        assert payload["sub"] == str(user_id)

    def test_refresh_token_no_role(self, token_service: TokenService):
        """Test that refresh token does not contain role claim"""
        user_id = UUID("12345678-1234-1234-1234-123456789012")

        token = token_service.create_refresh_token(user_id)
        payload = token_service.decode_token(token)

        assert "role" not in payload
        assert payload["type"] == "refresh"

    def test_token_type_distinction(self, token_service: TokenService):
        """Test that access and refresh tokens have different types"""
        user_id = UUID("12345678-1234-1234-1234-123456789012")

        access_token = token_service.create_access_token(
            user_id,
            additional_claims={"role": UserRole.USER.value}
        )
        refresh_token = token_service.create_refresh_token(user_id)

        access_payload = token_service.decode_token(access_token)
        refresh_payload = token_service.decode_token(refresh_token)

        assert access_payload["type"] == "access"
        assert refresh_payload["type"] == "refresh"

    def test_different_users_different_tokens(self, token_service: TokenService):
        """Test that different users get different tokens"""
        user1_id = UUID("12345678-1234-1234-1234-123456789011")
        user2_id = UUID("12345678-1234-1234-1234-123456789012")

        token1 = token_service.create_access_token(
            user1_id,
            additional_claims={"role": UserRole.USER.value}
        )
        token2 = token_service.create_access_token(
            user2_id,
            additional_claims={"role": UserRole.USER.value}
        )

        assert token1 != token2

        payload1 = token_service.decode_token(token1)
        payload2 = token_service.decode_token(token2)

        assert payload1["sub"] != payload2["sub"]

    def test_access_token_expiration_time(self, token_service: TokenService):
        """Test that access token has correct expiration time"""
        user_id = UUID("12345678-1234-1234-1234-123456789012")
        before = datetime.utcnow()

        token = token_service.create_access_token(
            user_id,
            additional_claims={"role": UserRole.USER.value}
        )
        payload = token_service.decode_token(token)

        after = datetime.utcnow()
        exp_time = datetime.utcfromtimestamp(payload["exp"])

        # Should expire approximately in 30 minutes
        expected_exp = before + timedelta(minutes=30)
        assert abs((exp_time - expected_exp).total_seconds()) < 5  # Within 5 seconds tolerance

    def test_all_user_roles_supported(self, token_service: TokenService):
        """Test that all user roles can be encoded in tokens"""
        user_id = UUID("12345678-1234-1234-1234-123456789012")

        for role in UserRole:
            token = token_service.create_access_token(
                user_id,
                additional_claims={"role": role.value}
            )
            payload = token_service.decode_token(token)

            assert payload["role"] == role.value

    def test_additional_claims_included(self, token_service: TokenService):
        """Test that additional claims are included in token"""
        user_id = UUID("12345678-1234-1234-1234-123456789012")

        token = token_service.create_access_token(
            user_id,
            additional_claims={
                "role": UserRole.ADMIN.value,
                "custom_claim": "custom_value"
            }
        )

        payload = token_service.decode_token(token)

        assert payload["role"] == UserRole.ADMIN.value
        assert payload["custom_claim"] == "custom_value"

    def test_verify_token_missing_sub(self, token_service: TokenService):
        """Test verifying token without sub claim raises error"""
        # Create token without sub
        payload = {
            "exp": datetime.utcnow() + timedelta(minutes=30),
            "type": "access"
        }
        invalid_token = jwt.encode(payload, token_service.secret_key, algorithm=token_service.algorithm)

        with pytest.raises(InvalidCredentialsError):
            token_service.verify_token(invalid_token)
