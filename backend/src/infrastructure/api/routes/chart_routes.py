"""
Chart Calculation API Routes

Endpoints for calculating and retrieving astrological charts.
"""
from typing import List
from fastapi import APIRouter, Depends, Query, status

from ....domain.entities.user import User
from ....application.dtos.chart_dtos import (
    CalculateNatalChartDTO,
    NatalChartDTO,
)
from ....application.use_cases.chart_calculation import (
    CalculateNatalChartUseCase,
    GetChartDetailsUseCase,
    ListClientChartsUseCase,
)
from ..dependencies.dependencies import (
    get_current_user,
    get_calculate_natal_chart_use_case,
    get_chart_details_use_case,
    get_list_client_charts_use_case,
)

router = APIRouter()


@router.post("/natal", response_model=NatalChartDTO, status_code=status.HTTP_201_CREATED)
async def calculate_natal_chart(
    chart_data: CalculateNatalChartDTO,
    current_user: User = Depends(get_current_user),
    use_case: CalculateNatalChartUseCase = Depends(get_calculate_natal_chart_use_case)
):
    """
    Calculate natal (birth) chart for a client.

    Performs astrological calculations and generates interpretations.
    """
    return use_case.execute(chart_data, current_user)


@router.get("/natal/{chart_id}", response_model=NatalChartDTO)
async def get_natal_chart(
    chart_id: str,
    current_user: User = Depends(get_current_user),
    use_case: GetChartDetailsUseCase = Depends(get_chart_details_use_case)
):
    """
    Get details of a previously calculated natal chart.

    User must have permission to view this chart.
    """
    return use_case.execute(chart_id, current_user)


@router.get("/client/{client_id}/charts", response_model=List[NatalChartDTO])
async def list_client_charts(
    client_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    use_case: ListClientChartsUseCase = Depends(get_list_client_charts_use_case)
):
    """
    List all charts for a specific client.

    Returns charts ordered by calculation date (newest first).
    """
    return use_case.execute(client_id, current_user, skip=skip, limit=limit)


# TODO: Add transits and solar return endpoints
# @router.post("/transits", ...)
# @router.post("/solar-return", ...)
