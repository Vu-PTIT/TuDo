from copy import deepcopy
from datetime import timedelta
from typing import Any
from uuid import UUID, uuid4

from fastapi import status

from app.core.config import get_settings
from app.core.errors import AppError
from app.infrastructure.supabase.client import TransactionalStore, utc_now


class SupportRepository:
    def __init__(self, store: TransactionalStore) -> None:
        self._store = store

    def create_request(
        self,
        owner_id: UUID,
        request_key: str,
        category: str,
        subject: str,
        description: str,
        diagnostics: dict[str, Any] | None,
    ) -> tuple[bool, dict[str, Any]]:
        cfg = get_settings()
        with self._store.lock:
            self._store.require_active_account(owner_id)
            if owner_id not in self._store.profiles:
                raise AppError(
                    code="PROFILE_NOT_READY",
                    message="Hồ sơ chưa được khởi tạo.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            for existing in self._store.support_requests.values():
                if (
                    existing["owner_id"] == owner_id
                    and existing["request_key"] == request_key
                ):
                    if (
                        existing["category"] != category
                        or existing["subject"] != subject
                        or existing["description"] != description
                        or existing.get("diagnostics") != diagnostics
                    ):
                        raise AppError(
                            code="CONFLICT",
                            message="Request key đã được sử dụng với nội dung phiếu hỗ trợ khác.",
                            status_code=status.HTTP_409_CONFLICT,
                        )
                    return False, deepcopy(existing)

            now = utc_now()
            cutoff_24h = now - timedelta(hours=24)
            recent = [
                r
                for r in self._store.support_requests.values()
                if r["owner_id"] == owner_id and r["created_at"] >= cutoff_24h
            ]
            if len(recent) >= cfg.support_daily_limit_per_user:
                oldest_in_window = min(r["created_at"] for r in recent)
                retry_after = int(
                    max(1, (oldest_in_window + timedelta(hours=24) - now).total_seconds())
                )
                raise AppError(
                    code="QUOTA_EXCEEDED",
                    message="Bạn đã đạt giới hạn gửi yêu cầu hỗ trợ trong ngày. Vui lòng thử lại sau.",
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    headers={"Retry-After": str(retry_after)},
                )

            req_id = uuid4()
            ref_code = f"SUP-{str(req_id)[:8].upper()}"
            row = {
                "id": req_id,
                "owner_id": owner_id,
                "reference_code": ref_code,
                "request_key": request_key,
                "category": category,
                "subject": subject,
                "description": description,
                "diagnostics": diagnostics,
                "status": "received",
                "created_at": now,
                "updated_at": now,
                "closed_at": None,
            }
            self._store.support_requests[req_id] = row
            return True, deepcopy(row)

    def list_requests(self, owner_id: UUID) -> list[dict[str, Any]]:
        with self._store.lock:
            rows = [
                deepcopy(r)
                for r in self._store.support_requests.values()
                if r["owner_id"] == owner_id
            ]
            rows.sort(key=lambda x: (x["created_at"], str(x["id"])), reverse=True)
            return rows

    def get_request(self, owner_id: UUID, request_id: UUID) -> dict[str, Any]:
        with self._store.lock:
            row = self._store.support_requests.get(request_id)
            if row is None or row["owner_id"] != owner_id:
                raise AppError(
                    code="NOT_FOUND",
                    message="Không tìm thấy phiếu hỗ trợ.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            return deepcopy(row)

