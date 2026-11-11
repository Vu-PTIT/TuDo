from typing import Literal
from uuid import UUID

from app.core.errors import PaginatedDataResponse, PaginatedMeta
from app.infrastructure.supabase.client import TransactionalStore
from app.modules.auth.schemas import AuthenticatedUser
from app.modules.wardrobe.repository import WardrobeRepository
from app.modules.wardrobe.schemas import (
    CreateWardrobeItemRequest,
    UpdateWardrobeItemRequest,
    WardrobeItemResponse,
)


def compute_cpw_metrics(
    purchase_price_vnd: int | None, wear_days_count: int
) -> tuple[float | None, int | None, Literal["calculated", "unworn", "missing_price"]]:
    if purchase_price_vnd is None:
        return None, None, "missing_price"
    if wear_days_count <= 0:
        return None, None, "unworn"
    if purchase_price_vnd == 0:
        return 0.0, 0, "calculated"
    raw_cpw = purchase_price_vnd / wear_days_count
    return raw_cpw, round(raw_cpw), "calculated"


class WardrobeService:
    def __init__(self, store: TransactionalStore) -> None:
        self._repo = WardrobeRepository(store)

    def _to_response(self, owner_id: UUID, row: dict) -> WardrobeItemResponse:
        wear_days = self._repo.count_distinct_wear_days(owner_id, row["id"])
        raw_cpw, display_cpw, cpw_status = compute_cpw_metrics(
            row.get("purchase_price_vnd"), wear_days
        )
        back_asset_id = row.get("back_asset_id")
        back_image_variant = row.get("back_image_variant")
        return WardrobeItemResponse(
            id=row["id"],
            name=row["name"],
            category=row["category"],
            source=row["source"],
            asset_id=row.get("asset_id"),
            image_variant=row.get("image_variant"),
            back_asset_id=back_asset_id,
            back_image_variant=back_image_variant,
            has_back_image=bool(back_asset_id and back_image_variant),
            colors=row.get("colors", []),
            size=row.get("size"),
            brand=row.get("brand"),
            purchase_price_vnd=row.get("purchase_price_vnd"),
            purchase_date=row.get("purchase_date"),
            notes=row.get("notes"),
            availability=row["availability"],
            wear_days_count=wear_days,
            cost_per_wear_vnd=raw_cpw,
            display_cost_per_wear_vnd=display_cpw,
            cpw_status=cpw_status,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def create_item(
        self, user: AuthenticatedUser, payload: CreateWardrobeItemRequest
    ) -> WardrobeItemResponse:
        row = self._repo.create_item(user.id, payload.model_dump())
        return self._to_response(user.id, row)

    def get_item(self, user: AuthenticatedUser, item_id: UUID) -> WardrobeItemResponse:
        row = self._repo.get_item_for_owner(user.id, item_id)
        return self._to_response(user.id, row)

    def list_items(
        self,
        user: AuthenticatedUser,
        q: str | None = None,
        category: str | None = None,
        color: str | None = None,
        availability: str | None = None,
        include_archived: bool = False,
        cursor: str | None = None,
        limit: int = 24,
    ) -> PaginatedDataResponse[WardrobeItemResponse]:
        all_rows = self._repo.list_items(
            owner_id=user.id,
            q=q,
            category=category,
            color=color,
            availability=availability,
            include_archived=include_archived,
        )
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
            data=[self._to_response(user.id, r) for r in sliced],
            meta=PaginatedMeta(
                next_cursor=next_cursor, has_more=has_more, total=len(all_rows)
            ),
        )

    def update_item(
        self,
        user: AuthenticatedUser,
        item_id: UUID,
        payload: UpdateWardrobeItemRequest,
    ) -> WardrobeItemResponse:
        updates = payload.model_dump(exclude_unset=True)
        row = self._repo.update_item(user.id, item_id, updates)
        return self._to_response(user.id, row)

    def delete_item(self, user: AuthenticatedUser, item_id: UUID) -> None:
        self._repo.soft_delete_item(user.id, item_id)

