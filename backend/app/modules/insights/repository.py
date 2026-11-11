from copy import deepcopy
from datetime import date
from typing import Any
from uuid import UUID

from app.infrastructure.supabase.client import TransactionalStore


class InsightsRepository:
    def __init__(self, store: TransactionalStore) -> None:
        self._store = store

    def get_summary_counts(self, owner_id: UUID) -> tuple[int, int, int]:
        with self._store.lock:
            active_items_count = sum(
                1
                for i in self._store.wardrobe_items.values()
                if i["owner_id"] == owner_id
                and i["deleted_at"] is None
                and i["availability"] != "archived"
            )
            active_outfits_count = sum(
                1
                for o in self._store.outfits.values()
                if o["owner_id"] == owner_id and o["deleted_at"] is None
            )
            # Total wear count is the count of distinct (item_id, worn_date) pairs across all wear logs
            item_date_pairs: set[tuple[UUID, date]] = set()
            for wl in self._store.wear_logs.values():
                if wl["owner_id"] != owner_id:
                    continue
                worn_date = wl["worn_date"]
                for li in self._store.wear_log_items.get(wl["id"], []):
                    item_date_pairs.add((li["item_id"], worn_date))

            return active_items_count, active_outfits_count, len(item_date_pairs)

    def get_items_and_wear_days(
        self, owner_id: UUID, include_archived: bool = False
    ) -> list[tuple[dict[str, Any], int]]:
        with self._store.lock:
            wear_dates_by_item: dict[UUID, set[date]] = {}
            for wl in self._store.wear_logs.values():
                if wl["owner_id"] != owner_id:
                    continue
                worn_date = wl["worn_date"]
                for li in self._store.wear_log_items.get(wl["id"], []):
                    wear_dates_by_item.setdefault(li["item_id"], set()).add(worn_date)

            results: list[tuple[dict[str, Any], int]] = []
            for item in self._store.wardrobe_items.values():
                if item["owner_id"] != owner_id or item["deleted_at"] is not None:
                    continue
                if not include_archived and item["availability"] == "archived":
                    continue
                days_count = len(wear_dates_by_item.get(item["id"], set()))
                results.append((deepcopy(item), days_count))

            return results

