from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status

from app.core.errors import DataResponse, PaginatedDataResponse
from app.infrastructure.supabase.client import TransactionalStore, get_store
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.schemas import AuthenticatedUser
from app.modules.outfits.schemas import (
    CreateOutfitRequest,
    OutfitResponse,
    UpdateOutfitRequest,
)
from app.modules.outfits.service import OutfitsService

router = APIRouter(prefix="/outfits", tags=["outfits"])


def get_outfits_service(
    store: Annotated[TransactionalStore, Depends(get_store)],
) -> OutfitsService:
    return OutfitsService(store)


@router.get("", response_model=PaginatedDataResponse[OutfitResponse])
async def list_outfits(
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[OutfitsService, Depends(get_outfits_service)],
    cursor: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedDataResponse[OutfitResponse]:
    return service.list_outfits(user, cursor=cursor, limit=limit)


@router.post(
    "",
    response_model=DataResponse[OutfitResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_outfit(
    payload: CreateOutfitRequest,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[OutfitsService, Depends(get_outfits_service)],
) -> DataResponse[OutfitResponse]:
    return DataResponse(data=service.create_outfit(user, payload))


@router.get("/{outfit_id}", response_model=DataResponse[OutfitResponse])
async def get_outfit(
    outfit_id: UUID,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[OutfitsService, Depends(get_outfits_service)],
) -> DataResponse[OutfitResponse]:
    return DataResponse(data=service.get_outfit(user, outfit_id))


@router.patch("/{outfit_id}", response_model=DataResponse[OutfitResponse])
async def update_outfit(
    outfit_id: UUID,
    payload: UpdateOutfitRequest,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[OutfitsService, Depends(get_outfits_service)],
) -> DataResponse[OutfitResponse]:
    return DataResponse(data=service.update_outfit(user, outfit_id, payload))


@router.delete("/{outfit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_outfit(
    outfit_id: UUID,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[OutfitsService, Depends(get_outfits_service)],
) -> Response:
    service.delete_outfit(user, outfit_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

