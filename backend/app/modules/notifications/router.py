from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.errors import DataResponse, PaginatedDataResponse
from app.infrastructure.supabase.client import TransactionalStore, get_store
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.schemas import AuthenticatedUser
from app.modules.notifications.schemas import (
    MarkAllReadResponse,
    NotificationResponse,
    UnreadCountResponse,
)
from app.modules.notifications.service import NotificationsService

router = APIRouter(prefix="/notifications", tags=["notifications"])


def get_notifications_service(
    store: Annotated[TransactionalStore, Depends(get_store)],
) -> NotificationsService:
    return NotificationsService(store)


@router.get("", response_model=PaginatedDataResponse[NotificationResponse])
async def list_notifications(
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[NotificationsService, Depends(get_notifications_service)],
    unread_only: Annotated[bool, Query()] = False,
    cursor: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedDataResponse[NotificationResponse]:
    return service.list_notifications(
        user, unread_only=unread_only, cursor=cursor, limit=limit
    )


@router.get("/unread-count", response_model=DataResponse[UnreadCountResponse])
async def get_unread_count(
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[NotificationsService, Depends(get_notifications_service)],
) -> DataResponse[UnreadCountResponse]:
    return DataResponse(data=service.get_unread_count(user))


@router.post("/read-all", response_model=DataResponse[MarkAllReadResponse])
async def mark_all_notifications_read(
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[NotificationsService, Depends(get_notifications_service)],
) -> DataResponse[MarkAllReadResponse]:
    return DataResponse(data=service.mark_all_read(user))


@router.post("/{notification_id}/read", response_model=DataResponse[NotificationResponse])
async def mark_notification_read(
    notification_id: UUID,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[NotificationsService, Depends(get_notifications_service)],
) -> DataResponse[NotificationResponse]:
    return DataResponse(data=service.mark_read(user, notification_id))

