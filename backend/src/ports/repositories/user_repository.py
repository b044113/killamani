"""
Port: UserRepository

Interface for User persistence operations.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from ...domain.entities.user import User, UserRole


class IUserRepository(ABC):
    """
    Repository interface for User entity.

    This is a port in hexagonal architecture - it defines what we need
    without specifying how it's implemented (adapter will implement this).
    """

    @abstractmethod
    def save(self, user: User) -> User:
        """
        Create or update a user.

        Args:
            user: User entity to save

        Returns:
            Saved user entity with updated fields

        Raises:
            DuplicateEntityError: If email already exists
            ValidationError: If user data is invalid
        """
        pass

    @abstractmethod
    def find_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Find user by ID.

        Args:
            user_id: UUID of the user

        Returns:
            User entity if found, None otherwise
        """
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        """
        Find user by email address.

        Args:
            email: Email address

        Returns:
            User entity if found, None otherwise
        """
        pass

    @abstractmethod
    def find_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Find all users with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of user entities
        """
        pass

    @abstractmethod
    def find_by_role(self, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Find users by role.

        Args:
            role: User role to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of user entities
        """
        pass

    @abstractmethod
    def find_consultants(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Find all consultants.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of consultant user entities
        """
        pass

    @abstractmethod
    def delete(self, user_id: UUID) -> bool:
        """
        Delete a user.

        Args:
            user_id: UUID of the user to delete

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        """
        Check if user exists by email.

        Args:
            email: Email address

        Returns:
            True if user exists, False otherwise
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """
        Count total number of users.

        Returns:
            Total count of users
        """
        pass

    @abstractmethod
    def count_by_role(self, role: UserRole) -> int:
        """
        Count users by role.

        Args:
            role: User role to count

        Returns:
            Count of users with specified role
        """
        pass
