from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status

from app.core.errors import DataResponse, PaginatedDataResponse
from app.infrastructure.supabase.client import TransactionalStore, get_store
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.schemas import AuthenticatedUser
from app.modules.wardrobe.schemas import (
    CreateWardrobeItemRequest,
    ItemAvailability,
    ItemCategory,
    UpdateWardrobeItemRequest,
    WardrobeItemResponse,
)
from app.modules.wardrobe.service import WardrobeService

router = APIRouter(prefix="/wardrobe/items", tags=["wardrobe"])


def get_wardrobe_service(
    store: Annotated[TransactionalStore, Depends(get_store)],
) -> WardrobeService:
    return WardrobeService(store)


@router.get("", response_model=PaginatedDataResponse[WardrobeItemResponse])
async def list_wardrobe_items(
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[WardrobeService, Depends(get_wardrobe_service)],
    q: Annotated[str | None, Query(max_length=100)] = None,
    category: Annotated[ItemCategory | None, Query()] = None,
    color: Annotated[str | None, Query(max_length=50)] = None,
    availability: Annotated[ItemAvailability | None, Query()] = None,
    include_archived: Annotated[bool, Query()] = False,
    cursor: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 24,
) -> PaginatedDataResponse[WardrobeItemResponse]:
    return service.list_items(
        user,
        q=q,
        category=category,
        color=color,
        availability=availability,
        include_archived=include_archived,
        cursor=cursor,
        limit=limit,
    )


@router.post(
    "",
    response_model=DataResponse[WardrobeItemResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_wardrobe_item(
    payload: CreateWardrobeItemRequest,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[WardrobeService, Depends(get_wardrobe_service)],
) -> DataResponse[WardrobeItemResponse]:
    return DataResponse(data=service.create_item(user, payload))


@router.get("/{item_id}", response_model=DataResponse[WardrobeItemResponse])
async def get_wardrobe_item(
    item_id: UUID,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[WardrobeService, Depends(get_wardrobe_service)],
) -> DataResponse[WardrobeItemResponse]:
    return DataResponse(data=service.get_item(user, item_id))


@router.patch("/{item_id}", response_model=DataResponse[WardrobeItemResponse])
async def update_wardrobe_item(
    item_id: UUID,
    payload: UpdateWardrobeItemRequest,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[WardrobeService, Depends(get_wardrobe_service)],
) -> DataResponse[WardrobeItemResponse]:
    return DataResponse(data=service.update_item(user, item_id, payload))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_wardrobe_item(
    item_id: UUID,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[WardrobeService, Depends(get_wardrobe_service)],
) -> Response:
    service.delete_item(user, item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

