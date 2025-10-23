"""
Unit tests for PasswordService
"""
import pytest
from src.application.services.password_service import PasswordService


@pytest.mark.unit
class TestPasswordService:
    """Test password hashing and verification"""

    def test_hash_password_creates_valid_hash(self, password_service: PasswordService):
        """Test that password hashing creates a valid bcrypt hash"""
        password = "my_secure_password123"
        hashed = password_service.hash_password(password)

        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != password
        assert hashed.startswith("$2b$")  # bcrypt prefix

    def test_verify_password_correct_password(self, password_service: PasswordService):
        """Test password verification with correct password"""
        password = "correct_password"
        hashed = password_service.hash_password(password)

        assert password_service.verify_password(password, hashed) is True

    def test_verify_password_incorrect_password(self, password_service: PasswordService):
        """Test password verification with incorrect password"""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = password_service.hash_password(password)

        assert password_service.verify_password(wrong_password, hashed) is False

    def test_verify_password_empty_password(self, password_service: PasswordService):
        """Test password verification with empty password"""
        password = "correct_password"
        hashed = password_service.hash_password(password)

        assert password_service.verify_password("", hashed) is False

    def test_hash_different_passwords_produce_different_hashes(
        self, password_service: PasswordService
    ):
        """Test that same password hashed twice produces different hashes (salt)"""
        password = "same_password"
        hash1 = password_service.hash_password(password)
        hash2 = password_service.hash_password(password)

        assert hash1 != hash2  # Different due to salt
        # But both should verify correctly
        assert password_service.verify_password(password, hash1) is True
        assert password_service.verify_password(password, hash2) is True

    def test_hash_password_with_special_characters(self, password_service: PasswordService):
        """Test password hashing with special characters"""
        password = "P@ssw0rd!#$%^&*()"
        hashed = password_service.hash_password(password)

        assert password_service.verify_password(password, hashed) is True

    def test_hash_password_with_unicode(self, password_service: PasswordService):
        """Test password hashing with unicode characters"""
        password = "contraseña_中文_🔐"
        hashed = password_service.hash_password(password)

        assert password_service.verify_password(password, hashed) is True

    def test_verify_password_case_sensitive(self, password_service: PasswordService):
        """Test that password verification is case sensitive"""
        password = "CaseSensitive"
        hashed = password_service.hash_password(password)

        assert password_service.verify_password("casesensitive", hashed) is False
        assert password_service.verify_password("CASESENSITIVE", hashed) is False
        assert password_service.verify_password(password, hashed) is True
