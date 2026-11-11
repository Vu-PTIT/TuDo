from datetime import timedelta
from uuid import UUID

from fastapi import status

from app.core.config import get_settings
from app.core.errors import AppError
from app.infrastructure.native.image_core import normalize_image_async
from app.infrastructure.supabase.client import TransactionalStore, utc_now
from app.modules.auth.schemas import AuthenticatedUser
from app.modules.media.repository import MediaRepository
from app.modules.media.schemas import (
    CreateReadUrlRequest,
    CreateUploadRequest,
    FinalizeUploadRequest,
    MediaAssetResponse,
    ReadUrlResponse,
    UploadGrantResponse,
    VariantMetadataSchema,
)

MIME_TO_EXT = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}

FORMAT_TO_MEDIA_TYPE = {
    "jpeg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
}


class MediaService:
    def __init__(self, store: TransactionalStore) -> None:
        self._store = store
        self._repo = MediaRepository(store)

    def _to_asset_response(self, row: dict) -> MediaAssetResponse:
        variants_raw = row.get("variant_metadata", {})
        variants: dict[str, VariantMetadataSchema] = {}
        available: list[str] = []
        for k in ("original", "cutout"):
            if k in variants_raw:
                available.append(k)
                meta = variants_raw[k]
                variants[k] = VariantMetadataSchema(
                    width=meta["width"],
                    height=meta["height"],
                    thumbnail_width=meta["thumbnail_width"],
                    thumbnail_height=meta["thumbnail_height"],
                    format=meta["format"],
                    has_alpha=meta["has_alpha"],
                )
        return MediaAssetResponse(
            id=row["id"],
            status=row["status"],
            available_variants=available,  # type: ignore[arg-type]
            variants=variants,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def create_upload_grant(
        self, user: AuthenticatedUser, payload: CreateUploadRequest
    ) -> UploadGrantResponse:
        ext = MIME_TO_EXT.get(payload.content_type, "jpg")
        row = self._repo.create_staging_asset(user.id, ext)
        asset_id = row["id"]
        upload_url = f"storage://wardrobe-media/{row['staging_path']}?token=upload-{asset_id}"
        return UploadGrantResponse(
            asset_id=asset_id,
            upload_url=upload_url,
            upload_expires_at=row["upload_expires_at"],
            status=row["status"],
        )

    async def finalize_upload(
        self,
        user: AuthenticatedUser,
        asset_id: UUID,
        payload: FinalizeUploadRequest | None = None,
    ) -> MediaAssetResponse:
        self._store.require_active_account(user.id)
        row = self._repo.get_asset_for_owner(user.id, asset_id)

        if row["status"] == "ready":
            return self._to_asset_response(row)
        if row["status"] == "rejected":
            raise AppError(
                code="INVALID_IMAGE",
                message="Tài nguyên ảnh này đã bị từ chối.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        cfg = get_settings()
        staging_path = row.get("staging_path")
        raw_bytes: bytes | None = None

        if payload is not None:
            try:
                raw_bytes = payload.decode_optional_bytes()
            except Exception as exc:
                raise AppError(
                    code="INVALID_IMAGE",
                    message="Dữ liệu ảnh gửi lên không hợp lệ.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                ) from exc

        if raw_bytes is None and staging_path:
            raw_bytes = self._store.get_storage_object(
                cfg.storage_bucket_wardrobe, staging_path
            )

        if not raw_bytes:
            raise AppError(
                code="INVALID_IMAGE",
                message="Chưa tìm thấy tập tin ảnh đã tải lên ở vùng staging.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            normalized = await normalize_image_async(raw_bytes)
        except AppError:
            if staging_path:
                self._store.delete_storage_object(cfg.storage_bucket_wardrobe, staging_path)
            self._repo.mark_asset_rejected(user.id, asset_id)
            raise

        # Check deletion tombstone before writing normalized objects
        self._store.require_active_account(user.id)

        ext = "jpg" if normalized.format == "jpeg" else normalized.format
        original_path = f"{user.id}/{asset_id}/original.{ext}"
        thumb_path = f"{user.id}/{asset_id}/original_thumb.{ext}"

        self._store.put_storage_object(
            cfg.storage_bucket_wardrobe, original_path, normalized.image_bytes
        )
        self._store.put_storage_object(
            cfg.storage_bucket_wardrobe, thumb_path, normalized.thumbnail_bytes
        )

        # Remove raw staging file containing metadata
        if staging_path:
            self._store.delete_storage_object(cfg.storage_bucket_wardrobe, staging_path)

        # Post-write check against concurrent account deletion
        if self._store.is_account_deleting(user.id):
            self._store.delete_storage_object(cfg.storage_bucket_wardrobe, original_path)
            self._store.delete_storage_object(cfg.storage_bucket_wardrobe, thumb_path)
            self._store.require_active_account(user.id)

        meta = {
            "width": normalized.width,
            "height": normalized.height,
            "thumbnail_width": normalized.thumbnail_width,
            "thumbnail_height": normalized.thumbnail_height,
            "format": normalized.format,
            "has_alpha": normalized.has_alpha,
            "thumbnail_path": thumb_path,
        }
        updated = self._repo.mark_asset_ready(user.id, asset_id, original_path, meta)
        return self._to_asset_response(updated)

    def create_read_url(
        self,
        user: AuthenticatedUser,
        asset_id: UUID,
        payload: CreateReadUrlRequest,
    ) -> ReadUrlResponse:
        cfg = get_settings()
        row = self._repo.get_asset_for_owner(user.id, asset_id)
        if row["status"] != "ready":
            raise AppError(
                code="INVALID_REQUEST",
                message="Ảnh chưa hoàn tất xử lý.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        variants = row.get("variant_metadata", {})
        if payload.variant not in variants:
            raise AppError(
                code="NOT_FOUND",
                message=f"Bản ảnh '{payload.variant}' không tồn tại cho món đồ này.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        expires_at = utc_now() + timedelta(seconds=cfg.signed_read_ttl_seconds)
        kind_part = "thumb" if payload.thumbnail else "full"
        url = (
            f"https://storage.closetloop.local/{cfg.storage_bucket_wardrobe}"
            f"/{asset_id}/{payload.variant}/{kind_part}?exp={int(expires_at.timestamp())}"
        )
        return ReadUrlResponse(
            asset_id=asset_id,
            variant=payload.variant,
            thumbnail=payload.thumbnail,
            url=url,
            expires_at=expires_at,
        )

    def download_media(
        self, user: AuthenticatedUser, asset_id: UUID, variant: str
    ) -> tuple[bytes, str, str]:
        self._store.require_active_account(user.id)
        if variant not in ("original", "cutout"):
            raise AppError(
                code="VALIDATION_ERROR",
                message="Variant tải ảnh chỉ chấp nhận 'original' hoặc 'cutout'.",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        row = self._repo.get_asset_for_owner(user.id, asset_id)
        if row["status"] != "ready":
            raise AppError(
                code="NOT_FOUND",
                message="Ảnh chưa sẵn sàng để tải xuống.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        path = row.get("original_path") if variant == "original" else row.get("cutout_path")
        variants = row.get("variant_metadata", {})
        if not path or variant not in variants:
            raise AppError(
                code="NOT_FOUND",
                message=f"Không tìm thấy bản ảnh '{variant}'.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        cfg = get_settings()
        content = self._store.get_storage_object(cfg.storage_bucket_wardrobe, path)
        if content is None:
            raise AppError(
                code="NOT_FOUND",
                message="Tập tin ảnh không tồn tại trong kho lưu trữ.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        fmt = variants[variant].get("format", "jpeg")
        ext = "jpg" if fmt == "jpeg" else fmt
        media_type = FORMAT_TO_MEDIA_TYPE.get(fmt, "application/octet-stream")
        filename = f"closet-loop-{asset_id}-{variant}.{ext}"
        return content, media_type, filename

