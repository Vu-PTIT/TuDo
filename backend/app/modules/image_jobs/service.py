from uuid import UUID

from fastapi import status

from app.core.config import get_settings
from app.core.errors import AppError
from app.infrastructure.ai.background_removal import (
    BackgroundRemovalProvider,
    PhotoroomBackgroundRemovalClient,
)
from app.infrastructure.native.image_core import validate_cutout_async
from app.infrastructure.supabase.client import TransactionalStore
from app.modules.accounts.repository import AccountsRepository
from app.modules.auth.schemas import AuthenticatedUser
from app.modules.image_jobs.repository import ImageJobsRepository
from app.modules.image_jobs.schemas import CreateImageJobRequest, ImageJobResponse
from app.modules.media.repository import MediaRepository


class ImageJobsService:
    def __init__(
        self,
        store: TransactionalStore,
        ai_provider: BackgroundRemovalProvider | None = None,
    ) -> None:
        self._store = store
        self._repo = ImageJobsRepository(store)
        self._media_repo = MediaRepository(store)
        self._accounts_repo = AccountsRepository(store)
        self._ai_provider = ai_provider or PhotoroomBackgroundRemovalClient()

    def _require_ai_consent(self, user_id: UUID) -> None:
        cfg = get_settings()
        latest = self._accounts_repo.get_latest_consent(user_id, "ai")
        if (
            latest is None
            or latest["action"] != "accepted"
            or latest["policy_version"] != cfg.current_ai_policy_version
        ):
            raise AppError(
                code="AI_CONSENT_REQUIRED",
                message="Cần chấp thuận thông báo xử lý ảnh bằng AI phiên bản hiện hành trước khi tách nền.",
                status_code=status.HTTP_403_FORBIDDEN,
                details={"required_ai_policy_version": cfg.current_ai_policy_version},
            )

    async def create_job(
        self, user: AuthenticatedUser, payload: CreateImageJobRequest
    ) -> ImageJobResponse:
        self._store.require_active_account(user.id)
        self._require_ai_consent(user.id)

        # Idempotent return if request_key already processed
        existing = self._repo.get_by_request_key(user.id, payload.request_key)
        if existing is not None:
            return ImageJobResponse(**existing)

        asset = self._media_repo.get_asset_for_owner(user.id, payload.asset_id)
        if asset["status"] != "ready" or not asset.get("original_path"):
            raise AppError(
                code="INVALID_REQUEST",
                message="Ảnh gốc phải ở trạng thái sẵn sàng trước khi tách nền.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        cfg = get_settings()
        original_bytes = self._store.get_storage_object(
            cfg.storage_bucket_wardrobe, asset["original_path"]
        )
        if not original_bytes:
            raise AppError(
                code="NOT_FOUND",
                message="Không tìm thấy dữ liệu ảnh gốc để xử lý.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        job = self._repo.create_processing_job(
            user.id, payload.asset_id, payload.request_key
        )
        if job["status"] != "processing":
            return ImageJobResponse(**job)

        job_id = job["id"]

        # Re-verify deletion status and profile existence before calling external paid provider
        if (
            self._store.is_account_deleting(user.id)
            or self._accounts_repo.get_profile(user.id) is None
        ):
            failed = self._repo.complete_job_failure(
                user.id, job_id, "ACCOUNT_DELETION_PENDING"
            )
            raise AppError(
                code="ACCOUNT_DELETION_PENDING",
                message="Tài khoản đang xóa, đã hủy yêu cầu tách nền.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        try:
            raw_cutout = await self._ai_provider.remove_background(original_bytes)
            validated = await validate_cutout_async(raw_cutout)
        except AppError as exc:
            failed = self._repo.complete_job_failure(user.id, job_id, exc.code)
            return ImageJobResponse(**failed)
        except Exception:
            failed = self._repo.complete_job_failure(
                user.id, job_id, "IMAGE_PROCESSING_FAILED"
            )
            return ImageJobResponse(**failed)

        # Check deletion status before writing cutout objects
        if self._store.is_account_deleting(user.id):
            self._repo.complete_job_failure(
                user.id, job_id, "ACCOUNT_DELETION_PENDING"
            )
            self._store.require_active_account(user.id)

        ext = "png" if validated.format == "png" else validated.format
        cutout_path = f"{user.id}/{payload.asset_id}/cutout.{ext}"
        cutout_thumb_path = f"{user.id}/{payload.asset_id}/cutout_thumb.{ext}"

        self._store.put_storage_object(
            cfg.storage_bucket_wardrobe, cutout_path, validated.image_bytes
        )
        self._store.put_storage_object(
            cfg.storage_bucket_wardrobe, cutout_thumb_path, validated.thumbnail_bytes
        )

        # Post-write race check against account deletion
        if self._store.is_account_deleting(user.id):
            self._store.delete_storage_object(cfg.storage_bucket_wardrobe, cutout_path)
            self._store.delete_storage_object(
                cfg.storage_bucket_wardrobe, cutout_thumb_path
            )
            self._repo.complete_job_failure(
                user.id, job_id, "ACCOUNT_DELETION_PENDING"
            )
            self._store.require_active_account(user.id)

        cutout_meta = {
            "width": validated.width,
            "height": validated.height,
            "thumbnail_width": validated.thumbnail_width,
            "thumbnail_height": validated.thumbnail_height,
            "format": validated.format,
            "has_alpha": validated.has_alpha,
            "thumbnail_path": cutout_thumb_path,
        }
        completed = self._repo.complete_job_success(
            user.id, job_id, payload.asset_id, cutout_path, cutout_meta
        )
        return ImageJobResponse(**completed)

    def get_job(self, user: AuthenticatedUser, job_id: UUID) -> ImageJobResponse:
        job = self._repo.get_job_for_owner(user.id, job_id)
        return ImageJobResponse(**job)

