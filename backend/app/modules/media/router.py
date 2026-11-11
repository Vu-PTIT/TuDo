from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Query, Response, status

from app.core.errors import DataResponse
from app.infrastructure.supabase.client import TransactionalStore, get_store
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.schemas import AuthenticatedUser
from app.modules.media.schemas import (
    CreateReadUrlRequest,
    CreateUploadRequest,
    FinalizeUploadRequest,
    MediaAssetResponse,
    ReadUrlResponse,
    UploadGrantResponse,
)
from app.modules.media.service import MediaService

router = APIRouter(prefix="/media", tags=["media"])


def get_media_service(
    store: Annotated[TransactionalStore, Depends(get_store)],
) -> MediaService:
    return MediaService(store)


@router.post(
    "/uploads",
    response_model=DataResponse[UploadGrantResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_media_upload(
    payload: CreateUploadRequest,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[MediaService, Depends(get_media_service)],
) -> DataResponse[UploadGrantResponse]:
    return DataResponse(data=service.create_upload_grant(user, payload))


@router.post(
    "/uploads/{asset_id}/finalize",
    response_model=DataResponse[MediaAssetResponse],
)
async def finalize_media_upload(
    asset_id: UUID,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[MediaService, Depends(get_media_service)],
    payload: Annotated[FinalizeUploadRequest | None, Body()] = None,
) -> DataResponse[MediaAssetResponse]:
    asset = await service.finalize_upload(user, asset_id, payload)
    return DataResponse(data=asset)


@router.post(
    "/{asset_id}/read-url",
    response_model=DataResponse[ReadUrlResponse],
)
async def create_media_read_url(
    asset_id: UUID,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[MediaService, Depends(get_media_service)],
    payload: Annotated[CreateReadUrlRequest | None, Body()] = None,
) -> DataResponse[ReadUrlResponse]:
    req = payload or CreateReadUrlRequest()
    return DataResponse(data=service.create_read_url(user, asset_id, req))


@router.get("/{asset_id}/download")
async def download_media_asset(
    asset_id: UUID,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[MediaService, Depends(get_media_service)],
    variant: Annotated[Literal["original", "cutout"], Query()] = "original",
) -> Response:
    content, media_type, filename = service.download_media(user, asset_id, variant)
    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Cache-Control": "private, no-store",
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )

