from uuid import UUID

from app.core.errors import PaginatedDataResponse, PaginatedMeta
from app.infrastructure.supabase.client import TransactionalStore
from app.modules.auth.schemas import AuthenticatedUser
from app.modules.notifications.repository import NotificationsRepository
from app.modules.notifications.schemas import (
    MarkAllReadResponse,
    NotificationResponse,
    UnreadCountResponse,
)

ALLOWED_ROUTES = {
    "settings_privacy": "/settings/privacy",
    "data_export": "/settings/privacy",
}


class NotificationsService:
    def __init__(self, store: TransactionalStore) -> None:
        self._repo = NotificationsRepository(store)

    def _to_response(self, row: dict) -> NotificationResponse:
        target_route = ALLOWED_ROUTES.get(row["target_type"], "/settings/privacy")
        return NotificationResponse(
            id=row["id"],
            type=row["type"],
            title=row["title"],
            body=row["body"],
            target_type=row["target_type"],
            target_id=row.get("target_id"),
            target_route=target_route,
            read_at=row.get("read_at"),
            created_at=row["created_at"],
        )

    def list_notifications(
        self,
        user: AuthenticatedUser,
        unread_only: bool = False,
        cursor: str | None = None,
        limit: int = 20,
    ) -> PaginatedDataResponse[NotificationResponse]:
        all_rows = self._repo.list_notifications(user.id, unread_only=unread_only)
        start_idx = 0
        if cursor:
            for idx, r in enumerate(all_rows):
                if str(r["id"]) == cursor:
                    start_idx = idx + 1
                    break
        sliced = all_rows[start_idx : start_idx + limit]
        has_more = (start_idx + limit) < len(all_rows)
        next_cursor = str(sliced[-1]["id"]) if has_more and sliced else None
        return PaginatedDataResponse(
            data=[self._to_response(r) for r in sliced],
            meta=PaginatedMeta(next_cursor=next_cursor, has_more=has_more),
        )

    def get_unread_count(self, user: AuthenticatedUser) -> UnreadCountResponse:
        return UnreadCountResponse(unread_count=self._repo.count_unread(user.id))

    def mark_read(
        self, user: AuthenticatedUser, notification_id: UUID
    ) -> NotificationResponse:
        row = self._repo.mark_read(user.id, notification_id)
        return self._to_response(row)

    def mark_all_read(self, user: AuthenticatedUser) -> MarkAllReadResponse:
        updated_count, cutoff = self._repo.mark_all_read(user.id)
        return MarkAllReadResponse(updated_count=updated_count, cutoff=cutoff)

