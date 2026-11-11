from copy import deepcopy
from datetime import date, datetime
from typing import Any
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

from fastapi import status

from app.core.errors import AppError
from app.infrastructure.supabase.client import TransactionalStore, utc_now


class PlannerRepository:
    def __init__(self, store: TransactionalStore) -> None:
        self._store = store

    def _build_snapshot_locked(
        self, owner_id: UUID, outfit_id: UUID
    ) -> dict[str, Any]:
        outfit = self._store.outfits.get(outfit_id)
        if (
            outfit is None
            or outfit["owner_id"] != owner_id
            or outfit["deleted_at"] is not None
        ):
            raise AppError(
                code="NOT_FOUND",
                message="Không tìm thấy outfit để lên lịch.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        canvas_items = self._store.outfit_items.get(outfit_id, [])
        if not canvas_items:
            raise AppError(
                code="INVALID_REQUEST",
                message="Outfit không chứa món đồ nào.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        snapshot_items: list[dict[str, Any]] = []
        for ci in sorted(canvas_items, key=lambda r: r["z_index"]):
            wi = self._store.wardrobe_items.get(ci["item_id"])
            if wi is None or wi["owner_id"] != owner_id:
                raise AppError(
                    code="INVALID_REQUEST",
                    message="Outfit chứa món đồ không thuộc tủ của bạn.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            if wi["deleted_at"] is not None or wi["availability"] == "archived":
                raise AppError(
                    code="INVALID_REQUEST",
                    message=f"Món đồ '{wi['name']}' đã xóa hoặc lưu trữ, vui lòng cập nhật outfit trước khi lên lịch.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            variant_meta = None
            asset_id = wi.get("asset_id")
            variant_key = wi.get("image_variant")
            if asset_id and variant_key:
                asset = self._store.media_assets.get(asset_id)
                if asset and asset["owner_id"] == owner_id:
                    variant_meta = deepcopy(
                        asset.get("variant_metadata", {}).get(variant_key)
                    )

            back_variant_meta = None
            back_asset_id = wi.get("back_asset_id")
            back_variant_key = wi.get("back_image_variant")
            if back_asset_id and back_variant_key:
                back_asset = self._store.media_assets.get(back_asset_id)
                if back_asset and back_asset["owner_id"] == owner_id:
                    back_variant_meta = deepcopy(
                        back_asset.get("variant_metadata", {}).get(back_variant_key)
                    )

            snapshot_items.append(
                {
                    "item_id": wi["id"],
                    "name": wi["name"],
                    "category": wi["category"],
                    "source": wi["source"],
                    "asset_id": asset_id,
                    "image_variant": variant_key,
                    "variant_metadata": variant_meta,
                    "back_asset_id": back_asset_id,
                    "back_image_variant": back_variant_key,
                    "back_variant_metadata": back_variant_meta,
                    "display_side": ci.get("display_side", "front"),
                    "x": ci["x"],
                    "y": ci["y"],
                    "w": ci["w"],
                    "h": ci["h"],
                    "z_index": ci["z_index"],
                }
            )

        return {
            "schema_version": 1,
            "outfit_id": outfit["id"],
            "outfit_name": outfit["name"],
            "items": snapshot_items,
        }

    def create_entry(
        self,
        owner_id: UUID,
        outfit_id: UUID,
        scheduled_date: date,
        event_label: str | None,
    ) -> dict[str, Any]:
        with self._store.lock:
            self._store.require_active_account(owner_id)
            if owner_id not in self._store.profiles:
                raise AppError(
                    code="PROFILE_NOT_READY",
                    message="Hồ sơ chưa được khởi tạo.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            snapshot = self._build_snapshot_locked(owner_id, outfit_id)
            now = utc_now()
            entry_id = uuid4()
            row = {
                "id": entry_id,
                "owner_id": owner_id,
                "outfit_id": outfit_id,
                "scheduled_date": scheduled_date,
                "event_label": event_label,
                "status": "planned",
                "outfit_snapshot": snapshot,
                "version": 1,
                "last_operation_key": None,
                "created_at": now,
                "updated_at": now,
            }
            self._store.planner_entries[entry_id] = row
            return deepcopy(row)

    def list_entries(
        self, owner_id: UUID, start_date: date, end_date: date
    ) -> list[dict[str, Any]]:
        with self._store.lock:
            rows = [
                deepcopy(e)
                for e in self._store.planner_entries.values()
                if e["owner_id"] == owner_id
                and start_date <= e["scheduled_date"] <= end_date
            ]
            rows.sort(key=lambda x: (x["scheduled_date"], x["created_at"], str(x["id"])))
            return rows

    def get_entry_for_owner(self, owner_id: UUID, entry_id: UUID) -> dict[str, Any]:
        with self._store.lock:
            row = self._store.planner_entries.get(entry_id)
            if row is None or row["owner_id"] != owner_id:
                raise AppError(
                    code="NOT_FOUND",
                    message="Không tìm thấy mục lịch mặc.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            return deepcopy(row)

    def update_entry(
        self,
        owner_id: UUID,
        entry_id: UUID,
        expected_version: int,
        updates: dict[str, Any],
    ) -> dict[str, Any]:
        with self._store.lock:
            self._store.require_active_account(owner_id)
            row = self._store.planner_entries.get(entry_id)
            if row is None or row["owner_id"] != owner_id:
                raise AppError(
                    code="NOT_FOUND",
                    message="Không tìm thấy mục lịch mặc.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            if row["version"] != expected_version:
                raise AppError(
                    code="CONFLICT",
                    message="Mục lịch đã thay đổi ở phiên khác. Vui lòng tải lại.",
                    status_code=status.HTTP_409_CONFLICT,
                )
            if row["status"] == "worn":
                raise AppError(
                    code="INVALID_REQUEST",
                    message="Mục lịch đã xác nhận mặc. Vui lòng hủy xác nhận trước khi chỉnh sửa.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            if "outfit_id" in updates and updates["outfit_id"] is not None:
                row["outfit_snapshot"] = self._build_snapshot_locked(
                    owner_id, updates["outfit_id"]
                )
                row["outfit_id"] = updates["outfit_id"]
                row["status"] = "planned"

            if "scheduled_date" in updates and updates["scheduled_date"] is not None:
                row["scheduled_date"] = updates["scheduled_date"]

            if updates.get("clear_event_label"):
                row["event_label"] = None
            elif "event_label" in updates and updates["event_label"] is not None:
                row["event_label"] = updates["event_label"]

            row["version"] += 1
            row["updated_at"] = utc_now()
            return deepcopy(row)

    def delete_entry(
        self,
        owner_id: UUID,
        entry_id: UUID,
        expected_version: int | None = None,
    ) -> None:
        with self._store.lock:
            self._store.require_active_account(owner_id)
            row = self._store.planner_entries.get(entry_id)
            if row is None or row["owner_id"] != owner_id:
                raise AppError(
                    code="NOT_FOUND",
                    message="Không tìm thấy mục lịch mặc.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            if expected_version is not None and row["version"] != expected_version:
                raise AppError(
                    code="CONFLICT",
                    message="Mục lịch đã thay đổi ở phiên khác. Vui lòng tải lại.",
                    status_code=status.HTTP_409_CONFLICT,
                )
            if row["status"] == "worn":
                raise AppError(
                    code="INVALID_REQUEST",
                    message="Mục lịch đã xác nhận mặc. Vui lòng hủy xác nhận trước khi xóa.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            del self._store.planner_entries[entry_id]

    def confirm_wear(
        self,
        owner_id: UUID,
        entry_id: UUID,
        operation_key: str,
        expected_version: int,
    ) -> dict[str, Any]:
        with self._store.lock:
            self._store.require_active_account(owner_id)
            row = self._store.planner_entries.get(entry_id)
            if row is None or row["owner_id"] != owner_id:
                raise AppError(
                    code="NOT_FOUND",
                    message="Không tìm thấy mục lịch mặc.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            # 1. Idempotency if operation_key matches the last committed operation
            if row.get("last_operation_key") == operation_key:
                return deepcopy(row)

            # 2. Optimistic concurrency check
            if row["version"] != expected_version:
                raise AppError(
                    code="CONFLICT",
                    message="Trạng thái mục lịch đã thay đổi. Vui lòng tải lại.",
                    status_code=status.HTTP_409_CONFLICT,
                )

            # 3. Date cannot be in the future according to user's profile timezone
            prof = self._store.profiles.get(owner_id)
            tz_name = prof["timezone"] if prof else "Asia/Ho_Chi_Minh"
            today_local = datetime.now(ZoneInfo(tz_name)).date()
            if row["scheduled_date"] > today_local:
                raise AppError(
                    code="INVALID_REQUEST",
                    message="Chỉ có thể xác nhận đã mặc cho hôm nay hoặc ngày trước đó theo múi giờ hồ sơ.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            # 4. If already worn, return current state without inserting duplicate logs
            if row["status"] == "worn":
                return deepcopy(row)

            # 5. Check all items in snapshot are currently available
            snapshot_items = row["outfit_snapshot"].get("items", [])
            unavailable_items: list[dict[str, str]] = []
            for s_item in snapshot_items:
                wi = self._store.wardrobe_items.get(s_item["item_id"])
                if wi is None or wi["owner_id"] != owner_id or wi["deleted_at"] is not None:
                    unavailable_items.append(
                        {"item_id": str(s_item["item_id"]), "name": s_item["name"], "reason": "deleted"}
                    )
                elif wi["availability"] in ("laundry", "unavailable", "archived"):
                    unavailable_items.append(
                        {
                            "item_id": str(s_item["item_id"]),
                            "name": wi["name"],
                            "reason": wi["availability"],
                        }
                    )

            if unavailable_items:
                raise AppError(
                    code="ITEM_UNAVAILABLE_FOR_WEAR",
                    message="Một hoặc nhiều món đồ trong mục lịch đang giặt, chưa sẵn sàng, lưu trữ hoặc đã xóa.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"unavailable_items": unavailable_items},
                )

            # 6. Insert wear_logs and wear_log_items in the same transaction
            now = utc_now()
            log_id = uuid4()
            for existing_wl in list(self._store.wear_logs.values()):
                if existing_wl["planner_entry_id"] == entry_id:
                    log_id = existing_wl["id"]
                    break
            else:
                self._store.wear_logs[log_id] = {
                    "id": log_id,
                    "owner_id": owner_id,
                    "planner_entry_id": entry_id,
                    "worn_date": row["scheduled_date"],
                    "created_at": now,
                }

            self._store.wear_log_items[log_id] = [
                {
                    "id": uuid4(),
                    "wear_log_id": log_id,
                    "owner_id": owner_id,
                    "item_id": s_item["item_id"],
                    "item_name_snapshot": s_item["name"],
                }
                for s_item in snapshot_items
            ]

            row["status"] = "worn"
            row["version"] += 1
            row["last_operation_key"] = operation_key
            row["updated_at"] = now
            return deepcopy(row)

    def unconfirm_wear(
        self,
        owner_id: UUID,
        entry_id: UUID,
        operation_key: str,
        expected_version: int,
    ) -> dict[str, Any]:
        with self._store.lock:
            self._store.require_active_account(owner_id)
            row = self._store.planner_entries.get(entry_id)
            if row is None or row["owner_id"] != owner_id:
                raise AppError(
                    code="NOT_FOUND",
                    message="Không tìm thấy mục lịch mặc.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            if row.get("last_operation_key") == operation_key:
                return deepcopy(row)

            if row["version"] != expected_version:
                raise AppError(
                    code="CONFLICT",
                    message="Trạng thái mục lịch đã thay đổi. Vui lòng tải lại.",
                    status_code=status.HTTP_409_CONFLICT,
                )

            # Delete wear log & items for this planner_entry_id
            to_delete = [
                wl_id
                for wl_id, wl in self._store.wear_logs.items()
                if wl["planner_entry_id"] == entry_id and wl["owner_id"] == owner_id
            ]
            for wl_id in to_delete:
                self._store.wear_logs.pop(wl_id, None)
                self._store.wear_log_items.pop(wl_id, None)

            row["status"] = "planned"
            row["version"] += 1
            row["last_operation_key"] = operation_key
            row["updated_at"] = utc_now()
            return deepcopy(row)

    def skip_entry(
        self,
        owner_id: UUID,
        entry_id: UUID,
        expected_version: int,
        operation_key: str | None = None,
    ) -> dict[str, Any]:
        with self._store.lock:
            self._store.require_active_account(owner_id)
            row = self._store.planner_entries.get(entry_id)
            if row is None or row["owner_id"] != owner_id:
                raise AppError(
                    code="NOT_FOUND",
                    message="Không tìm thấy mục lịch mặc.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            if operation_key and row.get("last_operation_key") == operation_key:
                return deepcopy(row)

            if row["version"] != expected_version:
                raise AppError(
                    code="CONFLICT",
                    message="Trạng thái mục lịch đã thay đổi. Vui lòng tải lại.",
                    status_code=status.HTTP_409_CONFLICT,
                )

            if row["status"] == "worn":
                raise AppError(
                    code="INVALID_REQUEST",
                    message="Mục lịch đã xác nhận mặc. Vui lòng hủy xác nhận trước khi bỏ qua.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            row["status"] = "skipped"
            row["version"] += 1
            if operation_key:
                row["last_operation_key"] = operation_key
            row["updated_at"] = utc_now()
            return deepcopy(row)

