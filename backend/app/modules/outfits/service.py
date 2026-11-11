from uuid import UUID

from app.core.errors import PaginatedDataResponse, PaginatedMeta
from app.infrastructure.supabase.client import TransactionalStore
from app.modules.auth.schemas import AuthenticatedUser
from app.modules.outfits.repository import OutfitsRepository
from app.modules.outfits.schemas import (
    CreateOutfitRequest,
    OutfitItemDetailResponse,
    OutfitResponse,
    UpdateOutfitRequest,
)


class OutfitsService:
    def __init__(self, store: TransactionalStore) -> None:
        self._store = store
        self._repo = OutfitsRepository(store)

    def _to_response(
        self, owner_id: UUID, outfit_row: dict, item_rows: list[dict]
    ) -> OutfitResponse:
        detailed_items: list[OutfitItemDetailResponse] = []
        has_missing = False

        with self._store.lock:
            for ir in item_rows:
                wi = self._store.wardrobe_items.get(ir["item_id"])
                if wi is None or wi["owner_id"] != owner_id or wi["deleted_at"] is not None:
                    has_missing = True
                    detailed_items.append(
                        OutfitItemDetailResponse(
                            item_id=ir["item_id"],
                            x=ir["x"],
                            y=ir["y"],
                            w=ir["w"],
                            h=ir["h"],
                            z_index=ir["z_index"],
                            display_side=ir.get("display_side", "front"),
                            item_name=wi["name"] if wi else None,
                            category=wi["category"] if wi else None,
                            source=wi["source"] if wi else None,
                            asset_id=wi.get("asset_id") if wi else None,
                            image_variant=wi.get("image_variant") if wi else None,
                            back_asset_id=wi.get("back_asset_id") if wi else None,
                            back_image_variant=wi.get("back_image_variant") if wi else None,
                            availability=wi.get("availability") if wi else None,
                            item_state="deleted",
                        )
                    )
                else:
                    avail = wi["availability"]
                    state_map = {
                        "available": "ready",
                        "laundry": "laundry",
                        "unavailable": "unavailable",
                        "archived": "archived",
                    }
                    item_state = state_map.get(avail, "ready")
                    if item_state != "ready":
                        has_missing = True
                    detailed_items.append(
                        OutfitItemDetailResponse(
                            item_id=ir["item_id"],
                            x=ir["x"],
                            y=ir["y"],
                            w=ir["w"],
                            h=ir["h"],
                            z_index=ir["z_index"],
                            display_side=ir.get("display_side", "front"),
                            item_name=wi["name"],
                            category=wi["category"],
                            source=wi["source"],
                            asset_id=wi.get("asset_id"),
                            image_variant=wi.get("image_variant"),
                            back_asset_id=wi.get("back_asset_id"),
                            back_image_variant=wi.get("back_image_variant"),
                            availability=avail,
                            item_state=item_state,  # type: ignore[arg-type]
                        )
                    )

        return OutfitResponse(
            id=outfit_row["id"],
            name=outfit_row["name"],
            notes=outfit_row.get("notes"),
            style_tags=outfit_row.get("style_tags", []),
            occasion_tags=outfit_row.get("occasion_tags", []),
            version=outfit_row["version"],
            items=detailed_items,
            has_missing_or_unavailable_items=has_missing,
            created_at=outfit_row["created_at"],
            updated_at=outfit_row["updated_at"],
        )

    def create_outfit(
        self, user: AuthenticatedUser, payload: CreateOutfitRequest
    ) -> OutfitResponse:
        outfit_row, item_rows = self._repo.create_outfit(
            owner_id=user.id,
            name=payload.name,
            notes=payload.notes,
            style_tags=payload.style_tags,
            occasion_tags=payload.occasion_tags,
            items=[i.model_dump() for i in payload.items],
        )
        return self._to_response(user.id, outfit_row, item_rows)

    def get_outfit(self, user: AuthenticatedUser, outfit_id: UUID) -> OutfitResponse:
        outfit_row, item_rows = self._repo.get_outfit_for_owner(user.id, outfit_id)
        return self._to_response(user.id, outfit_row, item_rows)

    def list_outfits(
        self, user: AuthenticatedUser, cursor: str | None = None, limit: int = 20
    ) -> PaginatedDataResponse[OutfitResponse]:
        all_pairs = self._repo.list_outfits(user.id)
        start_idx = 0
        if cursor:
            for idx, (o, _) in enumerate(all_pairs):
                if str(o["id"]) == cursor:
                    start_idx = idx + 1
                    break
        sliced = all_pairs[start_idx : start_idx + limit]
        has_more = (start_idx + limit) < len(all_pairs)
        next_cursor = str(sliced[-1][0]["id"]) if has_more and sliced else None
        return PaginatedDataResponse(
            data=[self._to_response(user.id, o, items) for o, items in sliced],
            meta=PaginatedMeta(
                next_cursor=next_cursor, has_more=has_more, total=len(all_pairs)
            ),
        )

    def update_outfit(
        self,
        user: AuthenticatedUser,
        outfit_id: UUID,
        payload: UpdateOutfitRequest,
    ) -> OutfitResponse:
        updates = payload.model_dump(exclude_unset=True)
        outfit_row, item_rows = self._repo.update_outfit(
            owner_id=user.id,
            outfit_id=outfit_id,
            expected_version=payload.expected_version,
            updates=updates,
        )
        return self._to_response(user.id, outfit_row, item_rows)

    def delete_outfit(self, user: AuthenticatedUser, outfit_id: UUID) -> None:
        self._repo.soft_delete_outfit(user.id, outfit_id)

