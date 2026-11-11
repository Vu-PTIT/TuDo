from copy import deepcopy
from typing import Any
from uuid import UUID, uuid4

from fastapi import status

from app.core.config import get_settings
from app.core.errors import AppError
from app.infrastructure.supabase.client import TransactionalStore, utc_now


class SettingsRepository:
    def __init__(self, store: TransactionalStore) -> None:
        self._store = store

    def get_settings(self, user_id: UUID) -> dict[str, Any]:
        with self._store.lock:
            row = self._store.user_settings.get(user_id)
            if row is None:
                raise AppError(
                    code="PROFILE_NOT_READY",
                    message="Cài đặt tài khoản chưa được khởi tạo.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            return deepcopy(row)

    def update_settings(
        self,
        user_id: UUID,
        expected_version: int,
        planner_default_view: str | None,
        activity_notifications: bool | None,
        analytics_opt_in: bool | None,
    ) -> dict[str, Any]:
        cfg = get_settings()
        with self._store.lock:
            self._store.require_active_account(user_id)
            row = self._store.user_settings.get(user_id)
            if row is None:
                raise AppError(
                    code="PROFILE_NOT_READY",
                    message="Cài đặt tài khoản chưa được khởi tạo.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            if row["version"] != expected_version:
                raise AppError(
                    code="CONFLICT",
                    message="Cài đặt đã thay đổi ở thiết bị hoặc tab khác. Vui lòng tải lại.",
                    status_code=status.HTTP_409_CONFLICT,
                )

            now = utc_now()
            next_version = row["version"] + 1

            # Record analytics consent event in the same transaction when analytics_opt_in changes
            if analytics_opt_in is not None and analytics_opt_in != row["analytics_opt_in"]:
                analytics_events = [
                    c
                    for c in self._store.account_consents
                    if c["owner_id"] == user_id and c["kind"] == "analytics"
                ]
                next_rev = (
                    max((c["revision"] for c in analytics_events), default=0) + 1
                )
                self._store.account_consents.append(
                    {
                        "id": uuid4(),
                        "owner_id": user_id,
                        "kind": "analytics",
                        "policy_version": cfg.current_analytics_policy_version,
                        "action": "accepted" if analytics_opt_in else "withdrawn",
                        "revision": next_rev,
                        "request_key": f"settings:analytics:v{next_version}",
                        "created_at": now,
                    }
                )
                row["analytics_opt_in"] = analytics_opt_in

            if planner_default_view is not None:
                row["planner_default_view"] = planner_default_view
            if activity_notifications is not None:
                row["activity_notifications"] = activity_notifications

            row["version"] = next_version
            row["updated_at"] = now
            return deepcopy(row)

