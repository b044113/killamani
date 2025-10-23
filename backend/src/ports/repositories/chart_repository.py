"""
Port: ChartRepository

Interface for Chart persistence operations (Natal, Transit, Solar Return).
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from ...domain.entities.natal_chart import NatalChart
from ...domain.entities.transit import Transit
from ...domain.entities.solar_return import SolarReturn


class INatalChartRepository(ABC):
    """Repository interface for NatalChart entity."""

    @abstractmethod
    def save(self, chart: NatalChart) -> NatalChart:
        """Save or update a natal chart."""
        pass

    @abstractmethod
    def find_by_id(self, chart_id: UUID) -> Optional[NatalChart]:
        """Find natal chart by ID."""
        pass

    @abstractmethod
    def find_by_client(
        self,
        client_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[NatalChart]:
        """Find all natal charts for a client."""
        pass

    @abstractmethod
    def find_latest_by_client(self, client_id: UUID) -> Optional[NatalChart]:
        """Find the most recent natal chart for a client."""
        pass

    @abstractmethod
    def delete(self, chart_id: UUID) -> bool:
        """Delete a natal chart."""
        pass

    @abstractmethod
    def count_by_client(self, client_id: UUID) -> int:
        """Count natal charts for a client."""
        pass


class ITransitRepository(ABC):
    """Repository interface for Transit entity."""

    @abstractmethod
    def save(self, transit: Transit) -> Transit:
        """Save or update a transit calculation."""
        pass

    @abstractmethod
    def find_by_id(self, transit_id: UUID) -> Optional[Transit]:
        """Find transit by ID."""
        pass

    @abstractmethod
    def find_by_client(
        self,
        client_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Transit]:
        """Find all transits for a client."""
        pass

    @abstractmethod
    def find_by_date_range(
        self,
        client_id: UUID,
        start_date: datetime,
        end_date: datetime
    ) -> List[Transit]:
        """Find transits for a client within a date range."""
        pass

    @abstractmethod
    def find_by_client_and_date(
        self,
        client_id: UUID,
        transit_date: datetime
    ) -> Optional[Transit]:
        """Find transit for a specific client and date."""
        pass

    @abstractmethod
    def delete(self, transit_id: UUID) -> bool:
        """Delete a transit."""
        pass

    @abstractmethod
    def count_by_client(self, client_id: UUID) -> int:
        """Count transits for a client."""
        pass


class ISolarReturnRepository(ABC):
    """Repository interface for SolarReturn entity."""

    @abstractmethod
    def save(self, solar_return: SolarReturn) -> SolarReturn:
        """Save or update a solar return chart."""
        pass

    @abstractmethod
    def find_by_id(self, solar_return_id: UUID) -> Optional[SolarReturn]:
        """Find solar return by ID."""
        pass

    @abstractmethod
    def find_by_client(
        self,
        client_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[SolarReturn]:
        """Find all solar returns for a client."""
        pass

    @abstractmethod
    def find_by_client_and_year(
        self,
        client_id: UUID,
        year: int
    ) -> Optional[SolarReturn]:
        """Find solar return for a specific client and year."""
        pass

    @abstractmethod
    def delete(self, solar_return_id: UUID) -> bool:
        """Delete a solar return."""
        pass

    @abstractmethod
    def count_by_client(self, client_id: UUID) -> int:
        """Count solar returns for a client."""
        pass
