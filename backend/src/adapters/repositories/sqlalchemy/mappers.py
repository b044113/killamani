"""
Entity-Model Mappers

Converts between domain entities and SQLAlchemy ORM models.
This maintains separation between domain and infrastructure layers.
"""
from typing import Optional

from ....domain.entities.user import User, UserRole
from ....domain.entities.client import Client
from ....domain.entities.natal_chart import NatalChart
from ....domain.entities.transit import Transit
from ....domain.entities.solar_return import SolarReturn
from ....domain.value_objects.birth_data import BirthData
from ....infrastructure.database.models import (
    UserModel,
    ClientModel,
    NatalChartModel,
    TransitModel,
    SolarReturnModel,
)


# ============================================================================
# User Mappers
# ============================================================================

def user_to_model(user: User) -> UserModel:
    """Convert User entity to UserModel."""
    return UserModel(
        id=user.id,
        email=user.email,
        hashed_password=user.hashed_password,
        role=user.role,
        is_active=user.is_active,
        is_first_login=user.is_first_login,
        preferred_language=user.preferred_language,
        consultant_id=user.consultant_id,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def model_to_user(model: UserModel) -> User:
    """Convert UserModel to User entity."""
    return User(
        id=model.id,
        email=model.email,
        hashed_password=model.hashed_password,
        role=model.role,
        is_active=model.is_active,
        is_first_login=model.is_first_login,
        preferred_language=model.preferred_language,
        consultant_id=model.consultant_id,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


# ============================================================================
# Client Mappers
# ============================================================================

def client_to_model(client: Client) -> ClientModel:
    """Convert Client entity to ClientModel."""
    # Handle optional birth_data
    birth_date = client.birth_data.date if client.birth_data else None
    birth_city = client.birth_data.city if client.birth_data else None
    birth_country = client.birth_data.country if client.birth_data else None
    birth_timezone = client.birth_data.timezone if client.birth_data else None
    birth_latitude = client.birth_data.latitude if client.birth_data else None
    birth_longitude = client.birth_data.longitude if client.birth_data else None

    return ClientModel(
        id=client.id,
        consultant_id=client.consultant_id,
        user_id=client.user_id,
        first_name=client.first_name,
        last_name=client.last_name,
        email=client.email,
        phone=client.phone,
        birth_date=birth_date,
        birth_city=birth_city,
        birth_country=birth_country,
        birth_timezone=birth_timezone,
        birth_latitude=birth_latitude,
        birth_longitude=birth_longitude,
        notes=client.notes,
        created_at=client.created_at,
        updated_at=client.updated_at,
    )


def model_to_client(model: ClientModel) -> Client:
    """Convert ClientModel to Client entity."""
    # Create BirthData only if birth data exists
    birth_data = None
    if model.birth_date and model.birth_city and model.birth_country and model.birth_timezone:
        birth_data = BirthData(
            date=model.birth_date,
            city=model.birth_city,
            country=model.birth_country,
            timezone=model.birth_timezone,
            latitude=model.birth_latitude,
            longitude=model.birth_longitude,
        )

    return Client(
        id=model.id,
        consultant_id=model.consultant_id,
        user_id=model.user_id,
        first_name=model.first_name,
        last_name=model.last_name,
        email=model.email,
        phone=model.phone,
        birth_data=birth_data,
        notes=model.notes,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


# ============================================================================
# NatalChart Mappers
# ============================================================================

def natal_chart_to_model(chart: NatalChart) -> NatalChartModel:
    """Convert NatalChart entity to NatalChartModel."""
    return NatalChartModel(
        id=chart.id,
        client_id=chart.client_id,
        name=chart.name,
        data=chart.data,
        solar_set=chart.solar_set,
        interpretations=chart.interpretations,
        house_system=chart.house_system,
        calculated_at=chart.calculated_at,
        svg_url=chart.svg_url,
        pdf_url=chart.pdf_url,
        created_at=chart.created_at,
        updated_at=chart.updated_at,
    )


def model_to_natal_chart(model: NatalChartModel) -> NatalChart:
    """Convert NatalChartModel to NatalChart entity."""
    return NatalChart(
        id=model.id,
        client_id=model.client_id,
        name=model.name,
        data=model.data,
        solar_set=model.solar_set,
        interpretations=model.interpretations,
        house_system=model.house_system,
        calculated_at=model.calculated_at,
        svg_url=model.svg_url,
        pdf_url=model.pdf_url,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


# ============================================================================
# Transit Mappers
# ============================================================================

def transit_to_model(transit: Transit) -> TransitModel:
    """Convert Transit entity to TransitModel."""
    return TransitModel(
        id=transit.id,
        client_id=transit.client_id,
        natal_chart_id=transit.natal_chart_id,
        transit_date=transit.transit_date,
        data=transit.data,
        significant_aspects=transit.significant_aspects,
        active_transits=transit.active_transits,
        interpretations=transit.interpretations,
        calculated_at=transit.calculated_at,
        created_at=transit.created_at,
        updated_at=transit.updated_at,
    )


def model_to_transit(model: TransitModel) -> Transit:
    """Convert TransitModel to Transit entity."""
    return Transit(
        id=model.id,
        client_id=model.client_id,
        natal_chart_id=model.natal_chart_id,
        transit_date=model.transit_date,
        data=model.data,
        significant_aspects=model.significant_aspects,
        active_transits=model.active_transits,
        interpretations=model.interpretations,
        calculated_at=model.calculated_at,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


# ============================================================================
# SolarReturn Mappers
# ============================================================================

def solar_return_to_model(solar_return: SolarReturn) -> SolarReturnModel:
    """Convert SolarReturn entity to SolarReturnModel."""
    return SolarReturnModel(
        id=solar_return.id,
        client_id=solar_return.client_id,
        natal_chart_id=solar_return.natal_chart_id,
        return_year=solar_return.return_year,
        return_datetime=solar_return.return_datetime,
        location_city=solar_return.location_city,
        location_country=solar_return.location_country,
        location_latitude=solar_return.location_latitude,
        location_longitude=solar_return.location_longitude,
        data=solar_return.data,
        solar_set=solar_return.solar_set,
        interpretations=solar_return.interpretations,
        house_system=solar_return.house_system,
        is_relocated=solar_return.is_relocated,
        calculated_at=solar_return.calculated_at,
        svg_url=solar_return.svg_url,
        pdf_url=solar_return.pdf_url,
        created_at=solar_return.created_at,
        updated_at=solar_return.updated_at,
    )


def model_to_solar_return(model: SolarReturnModel) -> SolarReturn:
    """Convert SolarReturnModel to SolarReturn entity."""
    return SolarReturn(
        id=model.id,
        client_id=model.client_id,
        natal_chart_id=model.natal_chart_id,
        return_year=model.return_year,
        return_datetime=model.return_datetime,
        location_city=model.location_city,
        location_country=model.location_country,
        location_latitude=model.location_latitude,
        location_longitude=model.location_longitude,
        data=model.data,
        solar_set=model.solar_set,
        interpretations=model.interpretations,
        house_system=model.house_system,
        is_relocated=model.is_relocated,
        calculated_at=model.calculated_at,
        svg_url=model.svg_url,
        pdf_url=model.pdf_url,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
