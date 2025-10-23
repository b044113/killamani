"""
SQLAlchemy User Repository Adapter

Implements IUserRepository using SQLAlchemy ORM.
"""
from typing import Optional, List
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ....domain.entities.user import User, UserRole
from ....domain.exceptions import DuplicateEntityError, ValidationError
from ....ports.repositories.user_repository import IUserRepository
from ....infrastructure.database.models import UserModel
from .mappers import user_to_model, model_to_user


class SQLAlchemyUserRepository(IUserRepository):
    """SQLAlchemy implementation of User repository."""

    def __init__(self, session: Session):
        self._session = session

    def save(self, user: User) -> User:
        """Create or update a user."""
        try:
            # Check if user exists
            existing = self._session.query(UserModel).filter_by(id=user.id).first()

            if existing:
                # Update existing user
                existing.email = user.email
                existing.hashed_password = user.hashed_password
                existing.role = user.role
                existing.is_active = user.is_active
                existing.is_first_login = user.is_first_login
                existing.preferred_language = user.preferred_language
                existing.consultant_id = user.consultant_id
                existing.updated_at = user.updated_at
                db_user = existing
            else:
                # Create new user
                db_user = user_to_model(user)
                self._session.add(db_user)

            self._session.commit()
            self._session.refresh(db_user)

            return model_to_user(db_user)

        except IntegrityError as e:
            self._session.rollback()
            if "email" in str(e.orig):
                raise DuplicateEntityError("User", "email", user.email)
            raise ValidationError(f"Database integrity error: {str(e)}")

    def find_by_id(self, user_id: UUID) -> Optional[User]:
        """Find user by ID."""
        db_user = self._session.query(UserModel).filter_by(id=user_id).first()
        return model_to_user(db_user) if db_user else None

    def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email address."""
        db_user = self._session.query(UserModel).filter_by(email=email).first()
        return model_to_user(db_user) if db_user else None

    def find_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Find all users with pagination."""
        db_users = (
            self._session.query(UserModel)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [model_to_user(db_user) for db_user in db_users]

    def find_by_role(self, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
        """Find users by role."""
        db_users = (
            self._session.query(UserModel)
            .filter_by(role=role)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [model_to_user(db_user) for db_user in db_users]

    def find_consultants(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Find all consultants."""
        return self.find_by_role(UserRole.CONSULTANT, skip, limit)

    def delete(self, user_id: UUID) -> bool:
        """Delete a user."""
        db_user = self._session.query(UserModel).filter_by(id=user_id).first()
        if not db_user:
            return False

        self._session.delete(db_user)
        self._session.commit()
        return True

    def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email."""
        count = self._session.query(UserModel).filter_by(email=email).count()
        return count > 0

    def count(self) -> int:
        """Count total number of users."""
        return self._session.query(UserModel).count()

    def count_by_role(self, role: UserRole) -> int:
        """Count users by role."""
        return self._session.query(UserModel).filter_by(role=role).count()
