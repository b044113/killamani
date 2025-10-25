"""
SQLAlchemy ORM Models

These are infrastructure-level database models that map to the database schema.
They are separate from domain entities to maintain clean architecture.
"""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Column, String, Boolean, DateTime, Integer, Float, Text, ForeignKey, Enum as SQLEnum, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .connection import Base
from ...domain.entities.user import UserRole


# ============================================================================
# User Model
# ============================================================================

class UserModel(Base):
    """SQLAlchemy model for User entity."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.USER)
    is_active = Column(Boolean, default=True, nullable=False)
    is_first_login = Column(Boolean, default=True, nullable=False)
    preferred_language = Column(String(10), default="en", nullable=False)
    consultant_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    clients = relationship("ClientModel", back_populates="consultant", foreign_keys="ClientModel.consultant_id")
    consultant = relationship("UserModel", remote_side=[id])

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


# ============================================================================
# Client Model
# ============================================================================

class ClientModel(Base):
    """SQLAlchemy model for Client entity."""
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    consultant_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)

    # Birth Data (now optional - charts are stored separately)
    birth_date = Column(DateTime, nullable=True)
    birth_city = Column(String(100), nullable=True)
    birth_country = Column(String(10), nullable=True)
    birth_timezone = Column(String(50), nullable=True)
    birth_latitude = Column(Float, nullable=True)
    birth_longitude = Column(Float, nullable=True)

    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    consultant = relationship("UserModel", foreign_keys=[consultant_id], back_populates="clients")
    user = relationship("UserModel", foreign_keys=[user_id])
    natal_charts = relationship("NatalChartModel", back_populates="client", cascade="all, delete-orphan")
    transits = relationship("TransitModel", back_populates="client", cascade="all, delete-orphan")
    solar_returns = relationship("SolarReturnModel", back_populates="client", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Client {self.first_name} {self.last_name}>"


# ============================================================================
# Natal Chart Model
# ============================================================================

class NatalChartModel(Base):
    """SQLAlchemy model for NatalChart entity."""
    __tablename__ = "natal_charts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)

    # Chart Information
    name = Column(String(200), default="Birth Chart", nullable=False)

    # Chart Data (stored as JSON)
    data = Column(JSON, nullable=False)
    solar_set = Column(JSON, nullable=False)
    interpretations = Column(JSON, default={}, nullable=False)

    # Metadata
    house_system = Column(String(20), default="placidus", nullable=False)
    calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Export URLs
    svg_url = Column(String(500), nullable=True)
    pdf_url = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    client = relationship("ClientModel", back_populates="natal_charts")

    def __repr__(self):
        return f"<NatalChart {self.id} for Client {self.client_id}>"


# ============================================================================
# Transit Model
# ============================================================================

class TransitModel(Base):
    """SQLAlchemy model for Transit entity."""
    __tablename__ = "transits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    natal_chart_id = Column(UUID(as_uuid=True), ForeignKey("natal_charts.id"), nullable=False)

    # Transit Data
    transit_date = Column(DateTime, nullable=False, index=True)
    data = Column(JSON, nullable=False)
    significant_aspects = Column(JSON, default=[], nullable=False)
    active_transits = Column(JSON, default=[], nullable=False)
    interpretations = Column(JSON, default={}, nullable=False)

    # Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    client = relationship("ClientModel", back_populates="transits")
    natal_chart = relationship("NatalChartModel")

    def __repr__(self):
        return f"<Transit {self.id} for {self.transit_date}>"


# ============================================================================
# Solar Return Model
# ============================================================================

class SolarReturnModel(Base):
    """SQLAlchemy model for SolarReturn entity."""
    __tablename__ = "solar_returns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    natal_chart_id = Column(UUID(as_uuid=True), ForeignKey("natal_charts.id"), nullable=False)

    # Solar Return Data
    return_year = Column(Integer, nullable=False, index=True)
    return_datetime = Column(DateTime, nullable=False)
    location_city = Column(String(100), nullable=False)
    location_country = Column(String(10), nullable=False)
    location_latitude = Column(Float, nullable=True)
    location_longitude = Column(Float, nullable=True)

    # Chart Data
    data = Column(JSON, nullable=False)
    solar_set = Column(JSON, nullable=False)
    interpretations = Column(JSON, default={}, nullable=False)

    # Metadata
    house_system = Column(String(20), default="placidus", nullable=False)
    is_relocated = Column(Boolean, default=False, nullable=False)
    calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Export URLs
    svg_url = Column(String(500), nullable=True)
    pdf_url = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    client = relationship("ClientModel", back_populates="solar_returns")
    natal_chart = relationship("NatalChartModel")

    def __repr__(self):
        return f"<SolarReturn {self.return_year} for Client {self.client_id}>"


# ============================================================================
# Audit Log Model
# ============================================================================

class AuditLogModel(Base):
    """SQLAlchemy model for Audit logs."""
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    audit_metadata = Column(JSON, default={}, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("UserModel")

    def __repr__(self):
        return f"<AuditLog {self.action} by {self.user_id} at {self.timestamp}>"
