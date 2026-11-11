from copy import deepcopy
from datetime import timedelta
from typing import Any
from uuid import UUID, uuid4

from fastapi import status

from app.core.config import get_settings
from app.core.errors import AppError
from app.infrastructure.supabase.client import TransactionalStore, utc_now


class ImageJobsRepository:
    def __init__(self, store: TransactionalStore) -> None:
        self._store = store

    def get_by_request_key(
        self, owner_id: UUID, request_key: str
    ) -> dict[str, Any] | None:
        with self._store.lock:
            for job in self._store.image_jobs.values():
                if job["owner_id"] == owner_id and job["request_key"] == request_key:
                    self._expire_stale_job_locked(job)
                    return deepcopy(job)
            return None

    def _expire_stale_job_locked(self, job: dict[str, Any]) -> None:
        if job["status"] == "processing":
            cfg = get_settings()
            now = utc_now()
            deadline = job["started_at"] + timedelta(seconds=cfg.ai_timeout_seconds + 2)
            if now >= deadline:
                job["status"] = "failed"
                job["error_code"] = "IMAGE_PROCESSING_TIMEOUT"
                job["finished_at"] = now

    def create_processing_job(
        self, owner_id: UUID, asset_id: UUID, request_key: str
    ) -> dict[str, Any]:
        cfg = get_settings()
        with self._store.lock:
            self._store.require_active_account(owner_id)

            existing = self.get_by_request_key(owner_id, request_key)
            if existing is not None:
                return existing

            now = utc_now()
            cutoff_24h = now - timedelta(hours=24)
            recent_jobs = [
                j
                for j in self._store.image_jobs.values()
                if j["owner_id"] == owner_id and j["started_at"] >= cutoff_24h
            ]
            if len(recent_jobs) >= cfg.ai_daily_quota_per_user:
                oldest = min(j["started_at"] for j in recent_jobs)
                retry_after = int(
                    max(1, (oldest + timedelta(hours=24) - now).total_seconds())
                )
                raise AppError(
                    code="QUOTA_EXCEEDED",
                    message="Bạn đã dùng hết lượt tách nền AI trong ngày. Bạn vẫn có thể lưu ảnh ban đầu.",
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    headers={"Retry-After": str(retry_after)},
                )

            job_id = uuid4()
            row = {
                "id": job_id,
                "owner_id": owner_id,
                "asset_id": asset_id,
                "request_key": request_key,
                "status": "processing",
                "error_code": None,
                "started_at": now,
                "finished_at": None,
            }
            self._store.image_jobs[job_id] = row
            return deepcopy(row)

    def complete_job_success(
        self,
        owner_id: UUID,
        job_id: UUID,
        asset_id: UUID,
        cutout_path: str,
        cutout_meta: dict[str, Any],
    ) -> dict[str, Any]:
        with self._store.lock:
            self._store.require_active_account(owner_id)
            job = self._store.image_jobs.get(job_id)
            asset = self._store.media_assets.get(asset_id)
            if job is None or asset is None or job["owner_id"] != owner_id:
                raise AppError(
                    code="NOT_FOUND",
                    message="Không tìm thấy tiến trình xử lý ảnh.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            now = utc_now()
            asset["cutout_path"] = cutout_path
            asset["variant_metadata"]["cutout"] = cutout_meta
            asset["updated_at"] = now

            job["status"] = "succeeded"
            job["error_code"] = None
            job["finished_at"] = now
            return deepcopy(job)

    def complete_job_failure(
        self, owner_id: UUID, job_id: UUID, error_code: str
    ) -> dict[str, Any]:
        with self._store.lock:
            job = self._store.image_jobs.get(job_id)
            if job is None or job["owner_id"] != owner_id:
                raise AppError(
                    code="NOT_FOUND",
                    message="Không tìm thấy tiến trình xử lý ảnh.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            job["status"] = "failed"
            job["error_code"] = error_code
            job["finished_at"] = utc_now()
            return deepcopy(job)

    def get_job_for_owner(self, owner_id: UUID, job_id: UUID) -> dict[str, Any]:
        with self._store.lock:
            job = self._store.image_jobs.get(job_id)
            if job is None or job["owner_id"] != owner_id:
                raise AppError(
                    code="NOT_FOUND",
                    message="Không tìm thấy tiến trình xử lý ảnh.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            self._expire_stale_job_locked(job)
            return deepcopy(job)

