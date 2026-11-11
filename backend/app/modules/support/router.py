from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status

from app.core.errors import DataResponse, PaginatedDataResponse
from app.infrastructure.supabase.client import TransactionalStore, get_store
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.schemas import AuthenticatedUser
from app.modules.support.schemas import CreateSupportRequest, SupportRequestResponse
from app.modules.support.service import SupportService

router = APIRouter(prefix="/support", tags=["support"])


def get_support_service(
    store: Annotated[TransactionalStore, Depends(get_store)],
) -> SupportService:
    return SupportService(store)


@router.post(
    "/requests",
    response_model=DataResponse[SupportRequestResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_support_request(
    payload: CreateSupportRequest,
    response: Response,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[SupportService, Depends(get_support_service)],
) -> DataResponse[SupportRequestResponse]:
    created, ticket = service.create_request(user, payload)
    response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return DataResponse(data=ticket)


@router.get(
    "/requests",
    response_model=PaginatedDataResponse[SupportRequestResponse],
)
async def list_support_requests(
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[SupportService, Depends(get_support_service)],
    cursor: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedDataResponse[SupportRequestResponse]:
    return service.list_requests(user, cursor=cursor, limit=limit)


@router.get(
    "/requests/{request_id}",
    response_model=DataResponse[SupportRequestResponse],
)
async def get_support_request_detail(
    request_id: UUID,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[SupportService, Depends(get_support_service)],
) -> DataResponse[SupportRequestResponse]:
    return DataResponse(data=service.get_request(user, request_id))

