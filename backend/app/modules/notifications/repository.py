from copy import deepcopy
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from fastapi import status

from app.core.errors import AppError
from app.infrastructure.supabase.client import TransactionalStore, utc_now


class NotificationsRepository:
    def __init__(self, store: TransactionalStore) -> None:
        self._store = store

    def create_notification_if_enabled(
        self,
        owner_id: UUID,
        event_key: str,
        notif_type: str,
        title: str,
        body: str,
        target_type: str,
        target_id: UUID | None = None,
    ) -> dict[str, Any] | None:
        """Create notification in the same transaction if activity_notifications is enabled and account is active."""
        with self._store.lock:
            if self._store.is_account_deleting(owner_id):
                return None
            settings = self._store.user_settings.get(owner_id)
            if settings is not None and not settings.get("activity_notifications", True):
                return None

            for existing in self._store.notifications.values():
                if existing["owner_id"] == owner_id and existing["event_key"] == event_key:
                    return deepcopy(existing)

            nid = uuid4()
            row = {
                "id": nid,
                "owner_id": owner_id,
                "event_key": event_key,
                "type": notif_type,
                "title": title,
                "body": body,
                "target_type": target_type,
                "target_id": target_id,
                "read_at": None,
                "created_at": utc_now(),
            }
            self._store.notifications[nid] = row
            return deepcopy(row)

    def list_notifications(
        self, owner_id: UUID, unread_only: bool = False
    ) -> list[dict[str, Any]]:
        with self._store.lock:
            rows = [
                deepcopy(n)
                for n in self._store.notifications.values()
                if n["owner_id"] == owner_id
                and (not unread_only or n["read_at"] is None)
            ]
            rows.sort(key=lambda x: (x["created_at"], str(x["id"])), reverse=True)
            return rows

    def count_unread(self, owner_id: UUID) -> int:
        with self._store.lock:
            return sum(
                1
                for n in self._store.notifications.values()
                if n["owner_id"] == owner_id and n["read_at"] is None
            )

    def mark_read(self, owner_id: UUID, notification_id: UUID) -> dict[str, Any]:
        with self._store.lock:
            self._store.require_active_account(owner_id)
            row = self._store.notifications.get(notification_id)
            if row is None or row["owner_id"] != owner_id:
                raise AppError(
                    code="NOT_FOUND",
                    message="Không tìm thấy thông báo.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            if row["read_at"] is None:
                row["read_at"] = utc_now()
            return deepcopy(row)

    def mark_all_read(self, owner_id: UUID) -> tuple[int, datetime]:
        with self._store.lock:
            self._store.require_active_account(owner_id)
            cutoff = utc_now()
            count = 0
            for row in self._store.notifications.values():
                if (
                    row["owner_id"] == owner_id
                    and row["read_at"] is None
                    and row["created_at"] <= cutoff
                ):
                    row["read_at"] = cutoff
                    count += 1
            return count, cutoff

