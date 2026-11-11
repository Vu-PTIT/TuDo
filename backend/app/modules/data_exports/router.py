from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status

from app.core.errors import DataResponse, PaginatedDataResponse
from app.infrastructure.supabase.client import TransactionalStore, get_store
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.schemas import AuthenticatedUser
from app.modules.data_exports.schemas import CreateDataExportRequest, DataExportResponse
from app.modules.data_exports.service import DataExportsService

router = APIRouter(prefix="/data-exports", tags=["data-exports"])


def get_data_exports_service(
    store: Annotated[TransactionalStore, Depends(get_store)],
) -> DataExportsService:
    return DataExportsService(store)


@router.post(
    "",
    response_model=DataResponse[DataExportResponse],
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_data_export(
    payload: CreateDataExportRequest,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[DataExportsService, Depends(get_data_exports_service)],
) -> DataResponse[DataExportResponse]:
    return DataResponse(data=service.create_export(user, payload))


@router.get(
    "",
    response_model=PaginatedDataResponse[DataExportResponse],
)
async def list_data_exports(
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[DataExportsService, Depends(get_data_exports_service)],
    cursor: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedDataResponse[DataExportResponse]:
    return service.list_exports(user, cursor=cursor, limit=limit)


@router.get(
    "/{export_id}",
    response_model=DataResponse[DataExportResponse],
)
async def get_data_export_detail(
    export_id: UUID,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[DataExportsService, Depends(get_data_exports_service)],
) -> DataResponse[DataExportResponse]:
    return DataResponse(data=service.get_export(user, export_id))


@router.get("/{export_id}/download")
async def download_data_export(
    export_id: UUID,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[DataExportsService, Depends(get_data_exports_service)],
) -> Response:
    content, filename = service.download_export(user, export_id)
    return Response(
        content=content,
        media_type="application/json",
        headers={
            "Cache-Control": "private, no-store",
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )

