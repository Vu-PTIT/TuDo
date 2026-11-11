from copy import deepcopy
from datetime import date
from typing import Any
from uuid import UUID, uuid4

from fastapi import status

from app.core.errors import AppError
from app.infrastructure.supabase.client import TransactionalStore, utc_now


class WardrobeRepository:
    def __init__(self, store: TransactionalStore) -> None:
        self._store = store

    def _verify_asset_ready_for_owner(
        self, owner_id: UUID, asset_id: UUID, image_variant: str
    ) -> None:
        asset = self._store.media_assets.get(asset_id)
        if asset is None or asset["owner_id"] != owner_id:
            raise AppError(
                code="NOT_FOUND",
                message="Không tìm thấy ảnh thuộc quyền sở hữu của bạn.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        if asset["status"] != "ready":
            raise AppError(
                code="INVALID_REQUEST",
                message="Ảnh chưa hoàn tất chuẩn hóa, chưa thể gắn vào món đồ.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        variants = asset.get("variant_metadata", {})
        if image_variant not in variants:
            raise AppError(
                code="INVALID_REQUEST",
                message=f"Bản ảnh '{image_variant}' chưa sẵn sàng cho tài nguyên này.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    def create_item(self, owner_id: UUID, data: dict[str, Any]) -> dict[str, Any]:
        with self._store.lock:
            self._store.require_active_account(owner_id)
            if owner_id not in self._store.profiles:
                raise AppError(
                    code="PROFILE_NOT_READY",
                    message="Hồ sơ chưa được khởi tạo.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            if data["source"] == "photo":
                self._verify_asset_ready_for_owner(
                    owner_id, data["asset_id"], data["image_variant"]
                )

            now = utc_now()
            item_id = uuid4()
            row = {
                "id": item_id,
                "owner_id": owner_id,
                "name": data["name"],
                "category": data["category"],
                "source": data["source"],
                "asset_id": data.get("asset_id"),
                "image_variant": data.get("image_variant"),
                "colors": list(data.get("colors") or []),
                "size": data.get("size"),
                "brand": data.get("brand"),
                "purchase_price_vnd": data.get("purchase_price_vnd"),
                "purchase_date": data.get("purchase_date"),
                "notes": data.get("notes"),
                "availability": data.get("availability", "available"),
                "deleted_at": None,
                "created_at": now,
                "updated_at": now,
            }
            self._store.wardrobe_items[item_id] = row
            return deepcopy(row)

    def get_item_for_owner(
        self, owner_id: UUID, item_id: UUID, include_deleted: bool = False
    ) -> dict[str, Any]:
        with self._store.lock:
            row = self._store.wardrobe_items.get(item_id)
            if (
                row is None
                or row["owner_id"] != owner_id
                or (not include_deleted and row["deleted_at"] is not None)
            ):
                raise AppError(
                    code="NOT_FOUND",
                    message="Không tìm thấy món đồ.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            return deepcopy(row)

    def list_items(
        self,
        owner_id: UUID,
        q: str | None = None,
        category: str | None = None,
        color: str | None = None,
        availability: str | None = None,
        include_archived: bool = False,
    ) -> list[dict[str, Any]]:
        with self._store.lock:
            results: list[dict[str, Any]] = []
            q_norm = q.strip().lower() if q else None
            color_norm = color.strip().lower() if color else None

            for row in self._store.wardrobe_items.values():
                if row["owner_id"] != owner_id or row["deleted_at"] is not None:
                    continue
                if availability:
                    if row["availability"] != availability:
                        continue
                elif not include_archived and row["availability"] == "archived":
                    continue

                if category and row["category"] != category:
                    continue
                if q_norm and q_norm not in row["name"].lower():
                    continue
                if color_norm and not any(
                    c.lower() == color_norm for c in row.get("colors", [])
                ):
                    continue
                results.append(deepcopy(row))

            results.sort(key=lambda x: (x["created_at"], str(x["id"])), reverse=True)
            return results

    def update_item(
        self, owner_id: UUID, item_id: UUID, updates: dict[str, Any]
    ) -> dict[str, Any]:
        with self._store.lock:
            self._store.require_active_account(owner_id)
            row = self._store.wardrobe_items.get(item_id)
            if row is None or row["owner_id"] != owner_id or row["deleted_at"] is not None:
                raise AppError(
                    code="NOT_FOUND",
                    message="Không tìm thấy món đồ.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            new_source = updates.get("source", row["source"])
            new_asset_id = updates.get("asset_id", row["asset_id"])
            new_variant = updates.get("image_variant", row["image_variant"])

            if new_source == "photo":
                if new_asset_id is None or new_variant is None:
                    raise AppError(
                        code="VALIDATION_ERROR",
                        message="Món đồ dùng ảnh bắt buộc phải có asset_id và image_variant.",
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    )
                self._verify_asset_ready_for_owner(owner_id, new_asset_id, new_variant)

            for field_name in (
                "name",
                "category",
                "source",
                "asset_id",
                "image_variant",
                "colors",
                "size",
                "brand",
                "purchase_date",
                "notes",
                "availability",
            ):
                if field_name in updates and updates[field_name] is not None:
                    row[field_name] = updates[field_name]

            if updates.get("clear_purchase_price"):
                row["purchase_price_vnd"] = None
            elif "purchase_price_vnd" in updates and updates["purchase_price_vnd"] is not None:
                row["purchase_price_vnd"] = updates["purchase_price_vnd"]

            row["updated_at"] = utc_now()
            return deepcopy(row)

    def soft_delete_item(self, owner_id: UUID, item_id: UUID) -> None:
        with self._store.lock:
            self._store.require_active_account(owner_id)
            row = self._store.wardrobe_items.get(item_id)
            if row is None or row["owner_id"] != owner_id or row["deleted_at"] is not None:
                raise AppError(
                    code="NOT_FOUND",
                    message="Không tìm thấy món đồ.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            now = utc_now()
            row["deleted_at"] = now
            row["updated_at"] = now

    def count_distinct_wear_days(self, owner_id: UUID, item_id: UUID) -> int:
        with self._store.lock:
            worn_dates: set[date] = set()
            for wl in self._store.wear_logs.values():
                if wl["owner_id"] != owner_id:
                    continue
                log_items = self._store.wear_log_items.get(wl["id"], [])
                if any(li["item_id"] == item_id for li in log_items):
                    worn_dates.add(wl["worn_date"])
            return len(worn_dates)

