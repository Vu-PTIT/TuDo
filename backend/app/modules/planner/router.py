from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status

from app.core.errors import DataResponse
from app.infrastructure.supabase.client import TransactionalStore, get_store
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.schemas import AuthenticatedUser
from app.modules.planner.schemas import (
    CreatePlannerEntryRequest,
    PlannerEntryResponse,
    SkipPlannerEntryRequest,
    UpdatePlannerEntryRequest,
    WearOperationRequest,
)
from app.modules.planner.service import PlannerService

router = APIRouter(prefix="/planner/entries", tags=["planner"])


def get_planner_service(
    store: Annotated[TransactionalStore, Depends(get_store)],
) -> PlannerService:
    return PlannerService(store)


@router.get("", response_model=DataResponse[list[PlannerEntryResponse]])
async def list_planner_entries(
    start_date: Annotated[date, Query()],
    end_date: Annotated[date, Query()],
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[PlannerService, Depends(get_planner_service)],
) -> DataResponse[list[PlannerEntryResponse]]:
    return DataResponse(data=service.list_entries(user, start_date, end_date))


@router.post(
    "",
    response_model=DataResponse[PlannerEntryResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_planner_entry(
    payload: CreatePlannerEntryRequest,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[PlannerService, Depends(get_planner_service)],
) -> DataResponse[PlannerEntryResponse]:
    return DataResponse(data=service.create_entry(user, payload))


@router.patch("/{entry_id}", response_model=DataResponse[PlannerEntryResponse])
async def update_planner_entry(
    entry_id: UUID,
    payload: UpdatePlannerEntryRequest,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[PlannerService, Depends(get_planner_service)],
) -> DataResponse[PlannerEntryResponse]:
    return DataResponse(data=service.update_entry(user, entry_id, payload))


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_planner_entry(
    entry_id: UUID,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[PlannerService, Depends(get_planner_service)],
    expected_version: Annotated[int | None, Query(ge=1)] = None,
) -> Response:
    service.delete_entry(user, entry_id, expected_version=expected_version)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{entry_id}/confirm-wear",
    response_model=DataResponse[PlannerEntryResponse],
)
async def confirm_planner_wear(
    entry_id: UUID,
    payload: WearOperationRequest,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[PlannerService, Depends(get_planner_service)],
) -> DataResponse[PlannerEntryResponse]:
    return DataResponse(data=service.confirm_wear(user, entry_id, payload))


@router.post(
    "/{entry_id}/unconfirm-wear",
    response_model=DataResponse[PlannerEntryResponse],
)
async def unconfirm_planner_wear(
    entry_id: UUID,
    payload: WearOperationRequest,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[PlannerService, Depends(get_planner_service)],
) -> DataResponse[PlannerEntryResponse]:
    return DataResponse(data=service.unconfirm_wear(user, entry_id, payload))


@router.post(
    "/{entry_id}/skip",
    response_model=DataResponse[PlannerEntryResponse],
)
async def skip_planner_entry(
    entry_id: UUID,
    payload: SkipPlannerEntryRequest,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[PlannerService, Depends(get_planner_service)],
) -> DataResponse[PlannerEntryResponse]:
    return DataResponse(data=service.skip_entry(user, entry_id, payload))

