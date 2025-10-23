"""
Port: ClientRepository

Interface for Client persistence operations.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from ...domain.entities.client import Client


class IClientRepository(ABC):
    """
    Repository interface for Client entity.

    This is a port in hexagonal architecture.
    """

    @abstractmethod
    def save(self, client: Client) -> Client:
        """
        Create or update a client.

        Args:
            client: Client entity to save

        Returns:
            Saved client entity with updated fields

        Raises:
            ValidationError: If client data is invalid
        """
        pass

    @abstractmethod
    def find_by_id(self, client_id: UUID) -> Optional[Client]:
        """
        Find client by ID.

        Args:
            client_id: UUID of the client

        Returns:
            Client entity if found, None otherwise
        """
        pass

    @abstractmethod
    def find_all(self, skip: int = 0, limit: int = 100) -> List[Client]:
        """
        Find all clients with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of client entities
        """
        pass

    @abstractmethod
    def find_by_consultant(
        self,
        consultant_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Client]:
        """
        Find all clients belonging to a consultant.

        Args:
            consultant_id: UUID of the consultant
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of client entities
        """
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Client]:
        """
        Find client by email address.

        Args:
            email: Email address

        Returns:
            Client entity if found, None otherwise
        """
        pass

    @abstractmethod
    def search(
        self,
        query: str,
        consultant_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Client]:
        """
        Search clients by name or email.

        Args:
            query: Search query string
            consultant_id: Optional consultant ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching client entities
        """
        pass

    @abstractmethod
    def delete(self, client_id: UUID) -> bool:
        """
        Delete a client.

        Args:
            client_id: UUID of the client to delete

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def count_by_consultant(self, consultant_id: UUID) -> int:
        """
        Count clients belonging to a consultant.

        Args:
            consultant_id: UUID of the consultant

        Returns:
            Count of clients
        """
        pass

    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        """
        Check if client exists by email.

        Args:
            email: Email address

        Returns:
            True if client exists, False otherwise
        """
        pass
