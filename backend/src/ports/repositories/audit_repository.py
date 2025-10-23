"""
Port: AuditRepository

Interface for Audit log persistence operations.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum


class AuditAction(str, Enum):
    """Audit action types"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    VIEW = "view"
    LOGIN = "login"
    LOGOUT = "logout"
    CALCULATE = "calculate"
    EXPORT = "export"


class AuditLog:
    """Audit log entry"""
    def __init__(
        self,
        user_id: UUID,
        action: AuditAction,
        entity_type: str,
        entity_id: Optional[UUID] = None,
        metadata: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        timestamp: Optional[datetime] = None,
    ):
        self.user_id = user_id
        self.action = action
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.metadata = metadata or {}
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.timestamp = timestamp or datetime.utcnow()


class IAuditRepository(ABC):
    """
    Repository interface for Audit logs.

    Tracks all user actions for security and compliance.
    """

    @abstractmethod
    def log(self, audit: AuditLog) -> AuditLog:
        """
        Create an audit log entry.

        Args:
            audit: Audit log entry

        Returns:
            Saved audit log
        """
        pass

    @abstractmethod
    def find_by_user(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        """
        Find audit logs for a specific user.

        Args:
            user_id: UUID of the user
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of audit logs
        """
        pass

    @abstractmethod
    def find_by_action(
        self,
        action: AuditAction,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        """
        Find audit logs by action type.

        Args:
            action: Action type
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of audit logs
        """
        pass

    @abstractmethod
    def find_by_entity(
        self,
        entity_type: str,
        entity_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        """
        Find audit logs for a specific entity.

        Args:
            entity_type: Type of entity (e.g., "Client", "Chart")
            entity_id: UUID of the entity
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of audit logs
        """
        pass

    @abstractmethod
    def find_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        user_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        """
        Find audit logs within a date range.

        Args:
            start_date: Start of date range
            end_date: End of date range
            user_id: Optional user ID filter
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of audit logs
        """
        pass

    @abstractmethod
    def count_by_user(self, user_id: UUID) -> int:
        """
        Count audit logs for a user.

        Args:
            user_id: UUID of the user

        Returns:
            Count of audit logs
        """
        pass

    @abstractmethod
    def count_by_action(self, action: AuditAction) -> int:
        """
        Count audit logs by action type.

        Args:
            action: Action type

        Returns:
            Count of audit logs
        """
        pass
