"""
SQLAlchemy Chart Repository Adapters

Implements chart repository interfaces using SQLAlchemy ORM.
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ....domain.entities.natal_chart import NatalChart
from ....domain.entities.transit import Transit
from ....domain.entities.solar_return import SolarReturn
from ....domain.exceptions import ValidationError
from ....ports.repositories.chart_repository import (
    INatalChartRepository,
    ITransitRepository,
    ISolarReturnRepository,
)
from ....infrastructure.database.models import (
    NatalChartModel,
    TransitModel,
    SolarReturnModel,
)
from .mappers import (
    natal_chart_to_model,
    model_to_natal_chart,
    transit_to_model,
    model_to_transit,
    solar_return_to_model,
    model_to_solar_return,
)


# ============================================================================
# Natal Chart Repository
# ============================================================================

class SQLAlchemyNatalChartRepository(INatalChartRepository):
    """SQLAlchemy implementation of NatalChart repository."""

    def __init__(self, session: Session):
        self._session = session

    def save(self, chart: NatalChart) -> NatalChart:
        """Save or update a natal chart."""
        try:
            existing = self._session.query(NatalChartModel).filter_by(id=chart.id).first()

            if existing:
                # Update existing chart
                existing.data = chart.data
                existing.solar_set = chart.solar_set
                existing.interpretations = chart.interpretations
                existing.house_system = chart.house_system
                existing.svg_url = chart.svg_url
                existing.pdf_url = chart.pdf_url
                existing.updated_at = chart.updated_at
                db_chart = existing
            else:
                # Create new chart
                db_chart = natal_chart_to_model(chart)
                self._session.add(db_chart)

            self._session.commit()
            self._session.refresh(db_chart)

            return model_to_natal_chart(db_chart)

        except IntegrityError as e:
            self._session.rollback()
            raise ValidationError(f"Database integrity error: {str(e)}")

    def find_by_id(self, chart_id: UUID) -> Optional[NatalChart]:
        """Find natal chart by ID."""
        db_chart = self._session.query(NatalChartModel).filter_by(id=chart_id).first()
        return model_to_natal_chart(db_chart) if db_chart else None

    def find_by_client(
        self,
        client_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[NatalChart]:
        """Find all natal charts for a client."""
        db_charts = (
            self._session.query(NatalChartModel)
            .filter_by(client_id=client_id)
            .order_by(NatalChartModel.calculated_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [model_to_natal_chart(db_chart) for db_chart in db_charts]

    def find_latest_by_client(self, client_id: UUID) -> Optional[NatalChart]:
        """Find the most recent natal chart for a client."""
        db_chart = (
            self._session.query(NatalChartModel)
            .filter_by(client_id=client_id)
            .order_by(NatalChartModel.calculated_at.desc())
            .first()
        )
        return model_to_natal_chart(db_chart) if db_chart else None

    def delete(self, chart_id: UUID) -> bool:
        """Delete a natal chart."""
        db_chart = self._session.query(NatalChartModel).filter_by(id=chart_id).first()
        if not db_chart:
            return False

        self._session.delete(db_chart)
        self._session.commit()
        return True

    def count_by_client(self, client_id: UUID) -> int:
        """Count natal charts for a client."""
        return self._session.query(NatalChartModel).filter_by(client_id=client_id).count()


# ============================================================================
# Transit Repository
# ============================================================================

class SQLAlchemyTransitRepository(ITransitRepository):
    """SQLAlchemy implementation of Transit repository."""

    def __init__(self, session: Session):
        self._session = session

    def save(self, transit: Transit) -> Transit:
        """Save or update a transit calculation."""
        try:
            existing = self._session.query(TransitModel).filter_by(id=transit.id).first()

            if existing:
                # Update existing transit
                existing.transit_date = transit.transit_date
                existing.data = transit.data
                existing.significant_aspects = transit.significant_aspects
                existing.active_transits = transit.active_transits
                existing.interpretations = transit.interpretations
                existing.updated_at = transit.updated_at
                db_transit = existing
            else:
                # Create new transit
                db_transit = transit_to_model(transit)
                self._session.add(db_transit)

            self._session.commit()
            self._session.refresh(db_transit)

            return model_to_transit(db_transit)

        except IntegrityError as e:
            self._session.rollback()
            raise ValidationError(f"Database integrity error: {str(e)}")

    def find_by_id(self, transit_id: UUID) -> Optional[Transit]:
        """Find transit by ID."""
        db_transit = self._session.query(TransitModel).filter_by(id=transit_id).first()
        return model_to_transit(db_transit) if db_transit else None

    def find_by_client(
        self,
        client_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Transit]:
        """Find all transits for a client."""
        db_transits = (
            self._session.query(TransitModel)
            .filter_by(client_id=client_id)
            .order_by(TransitModel.transit_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [model_to_transit(db_transit) for db_transit in db_transits]

    def find_by_date_range(
        self,
        client_id: UUID,
        start_date: datetime,
        end_date: datetime
    ) -> List[Transit]:
        """Find transits for a client within a date range."""
        db_transits = (
            self._session.query(TransitModel)
            .filter_by(client_id=client_id)
            .filter(TransitModel.transit_date >= start_date)
            .filter(TransitModel.transit_date <= end_date)
            .order_by(TransitModel.transit_date.asc())
            .all()
        )
        return [model_to_transit(db_transit) for db_transit in db_transits]

    def find_by_client_and_date(
        self,
        client_id: UUID,
        transit_date: datetime
    ) -> Optional[Transit]:
        """Find transit for a specific client and date."""
        db_transit = (
            self._session.query(TransitModel)
            .filter_by(client_id=client_id)
            .filter(TransitModel.transit_date == transit_date)
            .first()
        )
        return model_to_transit(db_transit) if db_transit else None

    def delete(self, transit_id: UUID) -> bool:
        """Delete a transit."""
        db_transit = self._session.query(TransitModel).filter_by(id=transit_id).first()
        if not db_transit:
            return False

        self._session.delete(db_transit)
        self._session.commit()
        return True

    def count_by_client(self, client_id: UUID) -> int:
        """Count transits for a client."""
        return self._session.query(TransitModel).filter_by(client_id=client_id).count()


# ============================================================================
# Solar Return Repository
# ============================================================================

class SQLAlchemySolarReturnRepository(ISolarReturnRepository):
    """SQLAlchemy implementation of SolarReturn repository."""

    def __init__(self, session: Session):
        self._session = session

    def save(self, solar_return: SolarReturn) -> SolarReturn:
        """Save or update a solar return chart."""
        try:
            existing = self._session.query(SolarReturnModel).filter_by(id=solar_return.id).first()

            if existing:
                # Update existing solar return
                existing.return_year = solar_return.return_year
                existing.return_datetime = solar_return.return_datetime
                existing.location_city = solar_return.location_city
                existing.location_country = solar_return.location_country
                existing.location_latitude = solar_return.location_latitude
                existing.location_longitude = solar_return.location_longitude
                existing.data = solar_return.data
                existing.solar_set = solar_return.solar_set
                existing.interpretations = solar_return.interpretations
                existing.house_system = solar_return.house_system
                existing.is_relocated = solar_return.is_relocated
                existing.svg_url = solar_return.svg_url
                existing.pdf_url = solar_return.pdf_url
                existing.updated_at = solar_return.updated_at
                db_solar_return = existing
            else:
                # Create new solar return
                db_solar_return = solar_return_to_model(solar_return)
                self._session.add(db_solar_return)

            self._session.commit()
            self._session.refresh(db_solar_return)

            return model_to_solar_return(db_solar_return)

        except IntegrityError as e:
            self._session.rollback()
            raise ValidationError(f"Database integrity error: {str(e)}")

    def find_by_id(self, solar_return_id: UUID) -> Optional[SolarReturn]:
        """Find solar return by ID."""
        db_solar_return = self._session.query(SolarReturnModel).filter_by(id=solar_return_id).first()
        return model_to_solar_return(db_solar_return) if db_solar_return else None

    def find_by_client(
        self,
        client_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[SolarReturn]:
        """Find all solar returns for a client."""
        db_solar_returns = (
            self._session.query(SolarReturnModel)
            .filter_by(client_id=client_id)
            .order_by(SolarReturnModel.return_year.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [model_to_solar_return(db_sr) for db_sr in db_solar_returns]

    def find_by_client_and_year(
        self,
        client_id: UUID,
        year: int
    ) -> Optional[SolarReturn]:
        """Find solar return for a specific client and year."""
        db_solar_return = (
            self._session.query(SolarReturnModel)
            .filter_by(client_id=client_id, return_year=year)
            .first()
        )
        return model_to_solar_return(db_solar_return) if db_solar_return else None

    def delete(self, solar_return_id: UUID) -> bool:
        """Delete a solar return."""
        db_solar_return = self._session.query(SolarReturnModel).filter_by(id=solar_return_id).first()
        if not db_solar_return:
            return False

        self._session.delete(db_solar_return)
        self._session.commit()
        return True

    def count_by_client(self, client_id: UUID) -> int:
        """Count solar returns for a client."""
        return self._session.query(SolarReturnModel).filter_by(client_id=client_id).count()
