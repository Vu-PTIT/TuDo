from uuid import UUID

from app.core.errors import PaginatedDataResponse, PaginatedMeta
from app.infrastructure.supabase.client import TransactionalStore
from app.modules.auth.schemas import AuthenticatedUser
from app.modules.support.repository import SupportRepository
from app.modules.support.schemas import (
    CreateSupportRequest,
    SupportDiagnosticsSchema,
    SupportRequestResponse,
)


class SupportService:
    def __init__(self, store: TransactionalStore) -> None:
        self._repo = SupportRepository(store)

    def _to_response(self, row: dict) -> SupportRequestResponse:
        diag = (
            SupportDiagnosticsSchema(**row["diagnostics"])
            if row.get("diagnostics")
            else None
        )
        return SupportRequestResponse(
            id=row["id"],
            reference_code=row["reference_code"],
            request_key=row["request_key"],
            category=row["category"],
            subject=row["subject"],
            description=row["description"],
            diagnostics=diag,
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            closed_at=row.get("closed_at"),
        )

    def create_request(
        self, user: AuthenticatedUser, payload: CreateSupportRequest
    ) -> tuple[bool, SupportRequestResponse]:
        diag_dict = (
            payload.diagnostics.model_dump(exclude_none=True)
            if payload.diagnostics is not None
            else None
        )
        created, row = self._repo.create_request(
            owner_id=user.id,
            request_key=payload.request_key,
            category=payload.category,
            subject=payload.subject,
            description=payload.description,
            diagnostics=diag_dict,
        )
        return created, self._to_response(row)

    def list_requests(
        self, user: AuthenticatedUser, cursor: str | None = None, limit: int = 20
    ) -> PaginatedDataResponse[SupportRequestResponse]:
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

    def get_request(
        self, user: AuthenticatedUser, request_id: UUID
    ) -> SupportRequestResponse:
        row = self._repo.get_request(user.id, request_id)
        return self._to_response(row)

