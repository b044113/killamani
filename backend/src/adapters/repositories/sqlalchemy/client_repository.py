"""
SQLAlchemy Client Repository Adapter

Implements IClientRepository using SQLAlchemy ORM.
"""
from typing import Optional, List
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

from ....domain.entities.client import Client
from ....domain.exceptions import ValidationError
from ....ports.repositories.client_repository import IClientRepository
from ....infrastructure.database.models import ClientModel
from .mappers import client_to_model, model_to_client


class SQLAlchemyClientRepository(IClientRepository):
    """SQLAlchemy implementation of Client repository."""

    def __init__(self, session: Session):
        self._session = session

    def save(self, client: Client) -> Client:
        """Create or update a client."""
        try:
            # Check if client exists
            existing = self._session.query(ClientModel).filter_by(id=client.id).first()

            if existing:
                # Update existing client
                existing.consultant_id = client.consultant_id
                existing.user_id = client.user_id
                existing.first_name = client.first_name
                existing.last_name = client.last_name
                existing.email = client.email
                existing.birth_date = client.birth_data.date
                existing.birth_city = client.birth_data.city
                existing.birth_country = client.birth_data.country
                existing.birth_timezone = client.birth_data.timezone
                existing.birth_latitude = client.birth_data.latitude
                existing.birth_longitude = client.birth_data.longitude
                existing.notes = client.notes
                existing.updated_at = client.updated_at
                db_client = existing
            else:
                # Create new client
                db_client = client_to_model(client)
                self._session.add(db_client)

            self._session.commit()
            self._session.refresh(db_client)

            return model_to_client(db_client)

        except IntegrityError as e:
            self._session.rollback()
            raise ValidationError(f"Database integrity error: {str(e)}")

    def find_by_id(self, client_id: UUID) -> Optional[Client]:
        """Find client by ID."""
        db_client = self._session.query(ClientModel).filter_by(id=client_id).first()
        return model_to_client(db_client) if db_client else None

    def find_all(self, skip: int = 0, limit: int = 100) -> List[Client]:
        """Find all clients with pagination."""
        db_clients = (
            self._session.query(ClientModel)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [model_to_client(db_client) for db_client in db_clients]

    def find_by_consultant(
        self,
        consultant_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Client]:
        """Find all clients belonging to a consultant."""
        db_clients = (
            self._session.query(ClientModel)
            .filter_by(consultant_id=consultant_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [model_to_client(db_client) for db_client in db_clients]

    def find_by_email(self, email: str) -> Optional[Client]:
        """Find client by email address."""
        db_client = self._session.query(ClientModel).filter_by(email=email).first()
        return model_to_client(db_client) if db_client else None

    def search(
        self,
        query: str,
        consultant_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Client]:
        """Search clients by name or email."""
        search_query = self._session.query(ClientModel).filter(
            or_(
                ClientModel.first_name.ilike(f"%{query}%"),
                ClientModel.last_name.ilike(f"%{query}%"),
                ClientModel.email.ilike(f"%{query}%")
            )
        )

        if consultant_id:
            search_query = search_query.filter_by(consultant_id=consultant_id)

        db_clients = search_query.offset(skip).limit(limit).all()
        return [model_to_client(db_client) for db_client in db_clients]

    def delete(self, client_id: UUID) -> bool:
        """Delete a client."""
        db_client = self._session.query(ClientModel).filter_by(id=client_id).first()
        if not db_client:
            return False

        self._session.delete(db_client)
        self._session.commit()
        return True

    def count_by_consultant(self, consultant_id: UUID) -> int:
        """Count clients belonging to a consultant."""
        return self._session.query(ClientModel).filter_by(consultant_id=consultant_id).count()

    def exists_by_email(self, email: str) -> bool:
        """Check if client exists by email."""
        count = self._session.query(ClientModel).filter_by(email=email).count()
        return count > 0
