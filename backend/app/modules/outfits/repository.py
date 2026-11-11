from copy import deepcopy
from typing import Any
from uuid import UUID, uuid4

from fastapi import status

from app.core.errors import AppError
from app.infrastructure.supabase.client import TransactionalStore, utc_now


class OutfitsRepository:
    def __init__(self, store: TransactionalStore) -> None:
        self._store = store

    def _validate_items_for_save(
        self, owner_id: UUID, items: list[dict[str, Any]]
    ) -> None:
        if not (1 <= len(items) <= 12):
            raise AppError(
                code="VALIDATION_ERROR",
                message="Outfit phải chứa từ 1 đến 12 món đồ.",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        for item_entry in items:
            wi = self._store.wardrobe_items.get(item_entry["item_id"])
            if wi is None or wi["owner_id"] != owner_id:
                raise AppError(
                    code="NOT_FOUND",
                    message="Một hoặc nhiều món đồ không tồn tại trong tủ của bạn.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            if wi["deleted_at"] is not None or wi["availability"] == "archived":
                raise AppError(
                    code="INVALID_REQUEST",
                    message=f"Món đồ '{wi['name']}' đã xóa hoặc đang lưu trữ, không thể thêm vào outfit.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

    def create_outfit(
        self,
        owner_id: UUID,
        name: str,
        notes: str | None,
        style_tags: list[str],
        occasion_tags: list[str],
        items: list[dict[str, Any]],
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        with self._store.lock:
            self._store.require_active_account(owner_id)
            if owner_id not in self._store.profiles:
                raise AppError(
                    code="PROFILE_NOT_READY",
                    message="Hồ sơ chưa được khởi tạo.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            self._validate_items_for_save(owner_id, items)

            now = utc_now()
            outfit_id = uuid4()
            outfit_row = {
                "id": outfit_id,
                "owner_id": owner_id,
                "name": name,
                "notes": notes,
                "style_tags": list(style_tags),
                "occasion_tags": list(occasion_tags),
                "version": 1,
                "deleted_at": None,
                "created_at": now,
                "updated_at": now,
            }
            item_rows = [
                {
                    "id": uuid4(),
                    "outfit_id": outfit_id,
                    "item_id": entry["item_id"],
                    "owner_id": owner_id,
                    "x": entry["x"],
                    "y": entry["y"],
                    "w": entry["w"],
                    "h": entry["h"],
                    "z_index": entry["z_index"],
                }
                for entry in items
            ]
            item_rows.sort(key=lambda r: r["z_index"])
            self._store.outfits[outfit_id] = outfit_row
            self._store.outfit_items[outfit_id] = item_rows
            return deepcopy(outfit_row), deepcopy(item_rows)

    def get_outfit_for_owner(
        self, owner_id: UUID, outfit_id: UUID
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        with self._store.lock:
            row = self._store.outfits.get(outfit_id)
            if row is None or row["owner_id"] != owner_id or row["deleted_at"] is not None:
                raise AppError(
                    code="NOT_FOUND",
                    message="Không tìm thấy outfit.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            items = deepcopy(self._store.outfit_items.get(outfit_id, []))
            items.sort(key=lambda r: r["z_index"])
            return deepcopy(row), items

    def list_outfits(
        self, owner_id: UUID
    ) -> list[tuple[dict[str, Any], list[dict[str, Any]]]]:
        with self._store.lock:
            outfits = [
                deepcopy(o)
                for o in self._store.outfits.values()
                if o["owner_id"] == owner_id and o["deleted_at"] is None
            ]
            outfits.sort(key=lambda x: (x["updated_at"], str(x["id"])), reverse=True)
            result = []
            for o in outfits:
                items = deepcopy(self._store.outfit_items.get(o["id"], []))
                items.sort(key=lambda r: r["z_index"])
                result.append((o, items))
            return result

    def update_outfit(
        self,
        owner_id: UUID,
        outfit_id: UUID,
        expected_version: int,
        updates: dict[str, Any],
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        with self._store.lock:
            self._store.require_active_account(owner_id)
            row = self._store.outfits.get(outfit_id)
            if row is None or row["owner_id"] != owner_id or row["deleted_at"] is not None:
                raise AppError(
                    code="NOT_FOUND",
                    message="Không tìm thấy outfit.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            if row["version"] != expected_version:
                raise AppError(
                    code="CONFLICT",
                    message="Outfit đã được sửa ở thiết bị hoặc tab khác. Vui lòng tải lại.",
                    status_code=status.HTTP_409_CONFLICT,
                )

            if "items" in updates and updates["items"] is not None:
                self._validate_items_for_save(owner_id, updates["items"])
                new_item_rows = [
                    {
                        "id": uuid4(),
                        "outfit_id": outfit_id,
                        "item_id": entry["item_id"],
                        "owner_id": owner_id,
                        "x": entry["x"],
                        "y": entry["y"],
                        "w": entry["w"],
                        "h": entry["h"],
                        "z_index": entry["z_index"],
                    }
                    for entry in updates["items"]
                ]
                new_item_rows.sort(key=lambda r: r["z_index"])
                self._store.outfit_items[outfit_id] = new_item_rows

            for field_name in ("name", "notes", "style_tags", "occasion_tags"):
                if field_name in updates and updates[field_name] is not None:
                    row[field_name] = updates[field_name]

            row["version"] += 1
            row["updated_at"] = utc_now()
            items = deepcopy(self._store.outfit_items.get(outfit_id, []))
            return deepcopy(row), items

    def soft_delete_outfit(self, owner_id: UUID, outfit_id: UUID) -> None:
        with self._store.lock:
            self._store.require_active_account(owner_id)
            row = self._store.outfits.get(outfit_id)
            if row is None or row["owner_id"] != owner_id or row["deleted_at"] is not None:
                raise AppError(
                    code="NOT_FOUND",
                    message="Không tìm thấy outfit.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            now = utc_now()
            row["deleted_at"] = now
            row["updated_at"] = now

