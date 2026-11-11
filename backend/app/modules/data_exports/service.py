from uuid import UUID

from fastapi import status

from app.core.config import get_settings
from app.core.errors import AppError, PaginatedDataResponse, PaginatedMeta
from app.infrastructure.supabase.client import TransactionalStore
from app.modules.auth.schemas import AuthenticatedUser
from app.modules.data_exports.repository import DataExportsRepository
from app.modules.data_exports.schemas import CreateDataExportRequest, DataExportResponse


class DataExportsService:
    def __init__(self, store: TransactionalStore) -> None:
        self._store = store
        self._repo = DataExportsRepository(store)

    def _to_response(self, row: dict) -> DataExportResponse:
        return DataExportResponse(
            id=row["id"],
            request_key=row["request_key"],
            status=row["status"],
            snapshot_at=row.get("snapshot_at"),
            expires_at=row.get("expires_at"),
            error_code=row.get("error_code"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def create_export(
        self, user: AuthenticatedUser, payload: CreateDataExportRequest
    ) -> DataExportResponse:
        _created, row = self._repo.create_request(user.id, payload.request_key)
        return self._to_response(row)

    def list_exports(
        self, user: AuthenticatedUser, cursor: str | None = None, limit: int = 20
    ) -> PaginatedDataResponse[DataExportResponse]:
        all_rows = self._repo.list_requests(user.id)
        start_idx = 0
        if cursor:
            for idx, r in enumerate(all_rows):
                if str(r["id"]) == cursor:
                    start_idx = idx + 1
                    break
        sliced = all_rows[start_idx : start_idx + limit]
        has_more = (start_idx + limit) < len(all_rows)
        next_cursor = str(sliced[-1]["id"]) if has_more and sliced else None
        return PaginatedDataResponse(
            data=[self._to_response(r) for r in sliced],
            meta=PaginatedMeta(next_cursor=next_cursor, has_more=has_more),
        )

    def get_export(self, user: AuthenticatedUser, export_id: UUID) -> DataExportResponse:
        row = self._repo.get_request_for_owner(user.id, export_id)
        return self._to_response(row)

    def download_export(self, user: AuthenticatedUser, export_id: UUID) -> tuple[bytes, str]:
        self._store.require_active_account(user.id)
        row = self._repo.get_request_for_owner(user.id, export_id)

        if row["status"] == "expired":
            raise AppError(
                code="EXPORT_EXPIRED",
                message="Bản sao dữ liệu đã hết hạn tải xuống. Vui lòng tạo yêu cầu mới.",
                status_code=status.HTTP_410_GONE,
            )

        if row["status"] != "ready" or not row.get("object_path"):
            raise AppError(
                code="CONFLICT",
                message="Bản sao dữ liệu chưa sẵn sàng để tải xuống.",
                status_code=status.HTTP_409_CONFLICT,
            )

        cfg = get_settings()
        content = self._store.get_storage_object(
            cfg.storage_bucket_exports, row["object_path"]
        )
        if content is None:
            raise AppError(
                code="EXPORT_EXPIRED",
                message="Tập tin bản sao dữ liệu không còn tồn tại.",
                status_code=status.HTTP_410_GONE,
            )

        filename = f"closet-loop-data-{export_id}.json"
        return content, filename

