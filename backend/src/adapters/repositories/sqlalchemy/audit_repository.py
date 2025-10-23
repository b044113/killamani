"""
SQLAlchemy Audit Repository Adapter

Implements IAuditRepository using SQLAlchemy ORM.
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ....domain.exceptions import ValidationError
from ....ports.repositories.audit_repository import IAuditRepository, AuditLog, AuditAction
from ....infrastructure.database.models import AuditLogModel


class SQLAlchemyAuditRepository(IAuditRepository):
    """SQLAlchemy implementation of Audit repository."""

    def __init__(self, session: Session):
        self._session = session

    def log(self, audit: AuditLog) -> AuditLog:
        """Create an audit log entry."""
        try:
            db_audit = AuditLogModel(
                user_id=audit.user_id,
                action=audit.action.value,
                entity_type=audit.entity_type,
                entity_id=audit.entity_id,
                metadata=audit.metadata,
                ip_address=audit.ip_address,
                user_agent=audit.user_agent,
                timestamp=audit.timestamp,
            )

            self._session.add(db_audit)
            self._session.commit()
            self._session.refresh(db_audit)

            return self._model_to_audit_log(db_audit)

        except IntegrityError as e:
            self._session.rollback()
            raise ValidationError(f"Database integrity error: {str(e)}")

    def find_by_user(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        """Find audit logs for a specific user."""
        db_audits = (
            self._session.query(AuditLogModel)
            .filter_by(user_id=user_id)
            .order_by(AuditLogModel.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._model_to_audit_log(db_audit) for db_audit in db_audits]

    def find_by_action(
        self,
        action: AuditAction,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        """Find audit logs by action type."""
        db_audits = (
            self._session.query(AuditLogModel)
            .filter_by(action=action.value)
            .order_by(AuditLogModel.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._model_to_audit_log(db_audit) for db_audit in db_audits]

    def find_by_entity(
        self,
        entity_type: str,
        entity_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        """Find audit logs for a specific entity."""
        db_audits = (
            self._session.query(AuditLogModel)
            .filter_by(entity_type=entity_type, entity_id=entity_id)
            .order_by(AuditLogModel.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._model_to_audit_log(db_audit) for db_audit in db_audits]

    def find_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        user_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        """Find audit logs within a date range."""
        query = self._session.query(AuditLogModel).filter(
            AuditLogModel.timestamp >= start_date,
            AuditLogModel.timestamp <= end_date
        )

        if user_id:
            query = query.filter_by(user_id=user_id)

        db_audits = (
            query
            .order_by(AuditLogModel.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._model_to_audit_log(db_audit) for db_audit in db_audits]

    def count_by_user(self, user_id: UUID) -> int:
        """Count audit logs for a user."""
        return self._session.query(AuditLogModel).filter_by(user_id=user_id).count()

    def count_by_action(self, action: AuditAction) -> int:
        """Count audit logs by action type."""
        return self._session.query(AuditLogModel).filter_by(action=action.value).count()

    def _model_to_audit_log(self, model: AuditLogModel) -> AuditLog:
        """Convert AuditLogModel to AuditLog."""
        return AuditLog(
            user_id=model.user_id,
            action=AuditAction(model.action),
            entity_type=model.entity_type,
            entity_id=model.entity_id,
            metadata=model.metadata,
            ip_address=model.ip_address,
            user_agent=model.user_agent,
            timestamp=model.timestamp,
        )
