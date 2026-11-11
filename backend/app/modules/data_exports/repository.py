from copy import deepcopy
from datetime import timedelta
from typing import Any
from uuid import UUID, uuid4

from fastapi import status

from app.core.errors import AppError
from app.infrastructure.supabase.client import TransactionalStore, utc_now


class DataExportsRepository:
    def __init__(self, store: TransactionalStore) -> None:
        self._store = store

    def create_request(self, user_id: UUID, request_key: str) -> tuple[bool, dict[str, Any]]:
        with self._store.lock:
            self._store.require_active_account(user_id)
            if user_id not in self._store.profiles:
                raise AppError(
                    code="PROFILE_NOT_READY",
                    message="Hồ sơ chưa được khởi tạo.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            # Idempotent check by request_key
            for req in self._store.data_export_requests.values():
                if req["owner_id"] == user_id and req["request_key"] == request_key:
                    return False, deepcopy(req)

            # Only one queued/running request per owner
            for req in self._store.data_export_requests.values():
                if req["owner_id"] == user_id and req["status"] in ("queued", "running"):
                    raise AppError(
                        code="CONFLICT",
                        message="Bạn đang có một yêu cầu chuẩn bị bản sao dữ liệu đang xử lý.",
                        status_code=status.HTTP_409_CONFLICT,
                    )

            # Rate limit: 1 new export per 24 hours
            now = utc_now()
            cutoff_24h = now - timedelta(hours=24)
            for req in self._store.data_export_requests.values():
                if (
                    req["owner_id"] == user_id
                    and req["status"] in ("ready", "expired")
                    and req["created_at"] >= cutoff_24h
                ):
                    retry_after = int(
                        max(1, (req["created_at"] + timedelta(hours=24) - now).total_seconds())
                    )
                    raise AppError(
                        code="QUOTA_EXCEEDED",
                        message="Mỗi tài khoản chỉ có thể tạo tối đa 1 bản sao dữ liệu mới trong 24 giờ.",
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        headers={"Retry-After": str(retry_after)},
                    )

            req_id = uuid4()
            record = {
                "id": req_id,
                "owner_id": user_id,
                "request_key": request_key,
                "status": "queued",
                "snapshot_at": None,
                "object_path": None,
                "expires_at": None,
                "error_code": None,
                "attempts": 0,
                "available_at": now,
                "lease_token": None,
                "lease_until": None,
                "created_at": now,
                "updated_at": now,
            }
            self._store.data_export_requests[req_id] = record
            return True, deepcopy(record)

    def list_requests(self, user_id: UUID) -> list[dict[str, Any]]:
        with self._store.lock:
            rows = [
                deepcopy(r)
                for r in self._store.data_export_requests.values()
                if r["owner_id"] == user_id
            ]
            rows.sort(key=lambda x: (x["created_at"], str(x["id"])), reverse=True)
            return rows

    def get_request_for_owner(self, user_id: UUID, export_id: UUID) -> dict[str, Any]:
        with self._store.lock:
            row = self._store.data_export_requests.get(export_id)
            if row is None or row["owner_id"] != user_id:
                raise AppError(
                    code="NOT_FOUND",
                    message="Không tìm thấy yêu cầu bản sao dữ liệu.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            now = utc_now()
            if (
                row["status"] == "ready"
                and row.get("expires_at") is not None
                and row["expires_at"] <= now
            ):
                row["status"] = "expired"
                row["updated_at"] = now
            return deepcopy(row)

