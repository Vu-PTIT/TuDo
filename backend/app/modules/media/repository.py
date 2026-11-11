from copy import deepcopy
from datetime import timedelta
from typing import Any
from uuid import UUID, uuid4

from fastapi import status

from app.core.config import get_settings
from app.core.errors import AppError
from app.infrastructure.supabase.client import TransactionalStore, utc_now


class MediaRepository:
    def __init__(self, store: TransactionalStore) -> None:
        self._store = store

    def create_staging_asset(self, owner_id: UUID, ext: str) -> dict[str, Any]:
        cfg = get_settings()
        with self._store.lock:
            self._store.require_active_account(owner_id)
            if owner_id not in self._store.profiles:
                raise AppError(
                    code="PROFILE_NOT_READY",
                    message="Hồ sơ chưa được khởi tạo.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            now = utc_now()
            asset_id = uuid4()
            staging_path = f"{owner_id}/{asset_id}/staging/upload.{ext}"
            upload_expires_at = now + timedelta(seconds=cfg.signed_upload_ttl_seconds)

            row = {
                "id": asset_id,
                "owner_id": owner_id,
                "staging_path": staging_path,
                "upload_expires_at": upload_expires_at,
                "original_path": None,
                "cutout_path": None,
                "variant_metadata": {},
                "status": "upload_pending",
                "created_at": now,
                "updated_at": now,
            }
            self._store.media_assets[asset_id] = row
            return deepcopy(row)

    def get_asset_for_owner(self, owner_id: UUID, asset_id: UUID) -> dict[str, Any]:
        with self._store.lock:
            row = self._store.media_assets.get(asset_id)
            if row is None or row["owner_id"] != owner_id:
                raise AppError(
                    code="NOT_FOUND",
                    message="Không tìm thấy tài nguyên ảnh.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            return deepcopy(row)

    def mark_asset_rejected(self, owner_id: UUID, asset_id: UUID) -> None:
        with self._store.lock:
            row = self._store.media_assets.get(asset_id)
            if row and row["owner_id"] == owner_id:
                row["status"] = "rejected"
                row["staging_path"] = None
                row["updated_at"] = utc_now()

    def mark_asset_ready(
        self,
        owner_id: UUID,
        asset_id: UUID,
        original_path: str,
        original_meta: dict[str, Any],
    ) -> dict[str, Any]:
        with self._store.lock:
            self._store.require_active_account(owner_id)
            row = self._store.media_assets.get(asset_id)
            if row is None or row["owner_id"] != owner_id:
                raise AppError(
                    code="NOT_FOUND",
                    message="Không tìm thấy tài nguyên ảnh.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            row["staging_path"] = None
            row["original_path"] = original_path
            row["variant_metadata"]["original"] = original_meta
            row["status"] = "ready"
            row["updated_at"] = utc_now()
            return deepcopy(row)

