from datetime import date
from uuid import UUID

from fastapi import status

from app.core.errors import AppError
from app.infrastructure.supabase.client import TransactionalStore
from app.modules.auth.schemas import AuthenticatedUser
from app.modules.planner.repository import PlannerRepository
from app.modules.planner.schemas import (
    CreatePlannerEntryRequest,
    LiveItemWarningSchema,
    OutfitSnapshotSchema,
    PlannerEntryResponse,
    SkipPlannerEntryRequest,
    UpdatePlannerEntryRequest,
    WearOperationRequest,
)


class PlannerService:
    def __init__(self, store: TransactionalStore) -> None:
        self._store = store
        self._repo = PlannerRepository(store)

    def _to_response(self, owner_id: UUID, row: dict) -> PlannerEntryResponse:
        snapshot = OutfitSnapshotSchema(**row["outfit_snapshot"])
        warnings: list[LiveItemWarningSchema] = []

        if row["status"] == "planned":
            with self._store.lock:
                for s_item in snapshot.items:
                    wi = self._store.wardrobe_items.get(s_item.item_id)
                    if wi is None or wi["owner_id"] != owner_id or wi["deleted_at"] is not None:
                        warnings.append(
                            LiveItemWarningSchema(
                                item_id=s_item.item_id,
                                item_name=s_item.name,
                                issue="deleted",
                            )
                        )
                    elif wi["availability"] in ("laundry", "unavailable", "archived"):
                        warnings.append(
                            LiveItemWarningSchema(
                                item_id=s_item.item_id,
                                item_name=wi["name"],
                                issue=wi["availability"],  # type: ignore[arg-type]
                            )
                        )

        return PlannerEntryResponse(
            id=row["id"],
            outfit_id=row.get("outfit_id"),
            scheduled_date=row["scheduled_date"],
            event_label=row.get("event_label"),
            status=row["status"],
            outfit_snapshot=snapshot,
            live_warnings=warnings,
            version=row["version"],
            last_operation_key=row.get("last_operation_key"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def list_entries(
        self, user: AuthenticatedUser, start_date: date, end_date: date
    ) -> list[PlannerEntryResponse]:
        if start_date > end_date:
            raise AppError(
                code="VALIDATION_ERROR",
                message="Ngày bắt đầu không được lớn hơn ngày kết thúc.",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        if (end_date - start_date).days > 93:
            raise AppError(
                code="VALIDATION_ERROR",
                message="Khoảng ngày truy vấn lịch tối đa là 93 ngày.",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        rows = self._repo.list_entries(user.id, start_date, end_date)
        return [self._to_response(user.id, r) for r in rows]

    def create_entry(
        self, user: AuthenticatedUser, payload: CreatePlannerEntryRequest
    ) -> PlannerEntryResponse:
        row = self._repo.create_entry(
            owner_id=user.id,
            outfit_id=payload.outfit_id,
            scheduled_date=payload.scheduled_date,
            event_label=payload.event_label,
        )
        return self._to_response(user.id, row)

    def update_entry(
        self,
        user: AuthenticatedUser,
        entry_id: UUID,
        payload: UpdatePlannerEntryRequest,
    ) -> PlannerEntryResponse:
        updates = payload.model_dump(exclude_unset=True)
        row = self._repo.update_entry(
            owner_id=user.id,
            entry_id=entry_id,
            expected_version=payload.expected_version,
            updates=updates,
        )
        return self._to_response(user.id, row)

    def delete_entry(
        self,
        user: AuthenticatedUser,
        entry_id: UUID,
        expected_version: int | None = None,
    ) -> None:
        self._repo.delete_entry(user.id, entry_id, expected_version)

    def confirm_wear(
        self,
        user: AuthenticatedUser,
        entry_id: UUID,
        payload: WearOperationRequest,
    ) -> PlannerEntryResponse:
        row = self._repo.confirm_wear(
            owner_id=user.id,
            entry_id=entry_id,
            operation_key=payload.operation_key,
            expected_version=payload.expected_version,
        )
        return self._to_response(user.id, row)

    def unconfirm_wear(
        self,
        user: AuthenticatedUser,
        entry_id: UUID,
        payload: WearOperationRequest,
    ) -> PlannerEntryResponse:
        row = self._repo.unconfirm_wear(
            owner_id=user.id,
            entry_id=entry_id,
            operation_key=payload.operation_key,
            expected_version=payload.expected_version,
        )
        return self._to_response(user.id, row)

    def skip_entry(
        self,
        user: AuthenticatedUser,
        entry_id: UUID,
        payload: SkipPlannerEntryRequest,
    ) -> PlannerEntryResponse:
        row = self._repo.skip_entry(
            owner_id=user.id,
            entry_id=entry_id,
            expected_version=payload.expected_version,
            operation_key=payload.operation_key,
        )
        return self._to_response(user.id, row)

