"""
Client Management API Routes

Endpoints for CRUD operations on clients.
"""
from typing import List
from fastapi import APIRouter, Depends, Query, status

from ....domain.entities.user import User
from ....application.dtos.client_dtos import (
    CreateClientDTO,
    UpdateClientDTO,
    SearchClientsDTO,
    ClientDTO,
    ClientListDTO,
)
from ....application.use_cases.client_management import (
    CreateClientUseCase,
    ListClientsUseCase,
    GetClientDetailsUseCase,
    UpdateClientUseCase,
    SearchClientsUseCase,
)
from ..dependencies.dependencies import (
    get_current_user,
    get_create_client_use_case,
    get_list_clients_use_case,
    get_client_details_use_case,
    get_update_client_use_case,
    get_search_clients_use_case,
)

router = APIRouter()


@router.post("/", response_model=ClientDTO, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: CreateClientDTO,
    current_user: User = Depends(get_current_user),
    use_case: CreateClientUseCase = Depends(get_create_client_use_case)
):
    """
    Create a new client.

    Only consultants and admins can create clients.
    """
    return use_case.execute(client_data, current_user)


@router.get("/", response_model=ClientListDTO)
async def list_clients(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    current_user: User = Depends(get_current_user),
    use_case: ListClientsUseCase = Depends(get_list_clients_use_case)
):
    """
    List all clients for the current user.

    Consultants see only their clients, admins see all.
    """
    return use_case.execute(current_user, skip=skip, limit=limit)


@router.get("/search", response_model=ClientListDTO)
async def search_clients(
    query: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    use_case: SearchClientsUseCase = Depends(get_search_clients_use_case)
):
    """
    Search clients by name or email.

    Returns matching clients based on user permissions.
    """
    search_dto = SearchClientsDTO(query=query, skip=skip, limit=limit)
    return use_case.execute(search_dto, current_user)


@router.get("/{client_id}", response_model=ClientDTO)
async def get_client(
    client_id: str,
    current_user: User = Depends(get_current_user),
    use_case: GetClientDetailsUseCase = Depends(get_client_details_use_case)
):
    """
    Get detailed information about a specific client.

    User must have permission to view this client.
    """
    return use_case.execute(client_id, current_user)


@router.put("/{client_id}", response_model=ClientDTO)
async def update_client(
    client_id: str,
    client_data: UpdateClientDTO,
    current_user: User = Depends(get_current_user),
    use_case: UpdateClientUseCase = Depends(get_update_client_use_case)
):
    """
    Update client information.

    User must have permission to update this client.
    """
    # Set client_id in DTO
    client_data.client_id = client_id
    return use_case.execute(client_data, current_user)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a client.

    User must have permission to delete this client.
    This endpoint is not yet fully implemented.
    """
    # TODO: Implement delete client use case
    return None
