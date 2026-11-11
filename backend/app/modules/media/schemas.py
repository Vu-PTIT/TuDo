import base64
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class VariantMetadataSchema(BaseModel):
    width: int
    height: int
    thumbnail_width: int
    thumbnail_height: int
    format: str
    has_alpha: bool


class CreateUploadRequest(BaseModel):
    filename: str = Field(default="upload.jpg", min_length=1, max_length=255)
    content_type: Literal["image/jpeg", "image/png", "image/webp"] = "image/jpeg"
    byte_size: int = Field(..., ge=1, le=10 * 1024 * 1024)


class UploadGrantResponse(BaseModel):
    asset_id: UUID
    upload_url: str
    upload_expires_at: datetime
    status: Literal["upload_pending", "ready", "rejected"]


class FinalizeUploadRequest(BaseModel):
    """Optional inline base64 content for local development/testing when not uploading directly to Supabase Storage."""

    staged_bytes_b64: str | None = None

    def decode_optional_bytes(self) -> bytes | None:
        if not self.staged_bytes_b64:
            return None
        return base64.b64decode(self.staged_bytes_b64)


class MediaAssetResponse(BaseModel):
    id: UUID
    status: Literal["upload_pending", "ready", "rejected"]
    available_variants: list[Literal["original", "cutout"]]
    variants: dict[str, VariantMetadataSchema]
    created_at: datetime
    updated_at: datetime


class CreateReadUrlRequest(BaseModel):
    variant: Literal["original", "cutout"] = "original"
    thumbnail: bool = False


class ReadUrlResponse(BaseModel):
    asset_id: UUID
    variant: Literal["original", "cutout"]
    thumbnail: bool
    url: str
    expires_at: datetime

