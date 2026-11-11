from typing import Literal

from app.core.errors import PaginatedDataResponse, PaginatedMeta
from app.infrastructure.supabase.client import TransactionalStore
from app.modules.auth.schemas import AuthenticatedUser
from app.modules.insights.repository import InsightsRepository
from app.modules.insights.schemas import (
    CostPerWearItemResponse,
    InsightsSummaryResponse,
)
from app.modules.wardrobe.service import compute_cpw_metrics


class InsightsService:
    def __init__(self, store: TransactionalStore) -> None:
        self._repo = InsightsRepository(store)

    def get_summary(self, user: AuthenticatedUser) -> InsightsSummaryResponse:
        active_items, active_outfits, total_wears = self._repo.get_summary_counts(
            user.id
        )
        return InsightsSummaryResponse(
            active_items_count=active_items,
            active_outfits_count=active_outfits,
            total_wear_count=total_wears,
        )

    def list_cost_per_wear(
        self,
        user: AuthenticatedUser,
        include_archived: bool = False,
        sort: Literal["cpw_asc", "cpw_desc", "wears_desc", "wears_asc"] = "cpw_asc",
        cursor: str | None = None,
        limit: int = 24,
    ) -> PaginatedDataResponse[CostPerWearItemResponse]:
        pairs = self._repo.get_items_and_wear_days(
            user.id, include_archived=include_archived
        )
        items: list[CostPerWearItemResponse] = []
        for row, wear_days in pairs:
            raw_cpw, display_cpw, cpw_status = compute_cpw_metrics(
                row.get("purchase_price_vnd"), wear_days
            )
            items.append(
                CostPerWearItemResponse(
                    item_id=row["id"],
                    name=row["name"],
                    category=row["category"],
                    source=row["source"],
                    asset_id=row.get("asset_id"),
                    image_variant=row.get("image_variant"),
                    availability=row["availability"],
                    purchase_price_vnd=row.get("purchase_price_vnd"),
                    wear_days_count=wear_days,
                    cost_per_wear_vnd=raw_cpw,
                    display_cost_per_wear_vnd=display_cpw,
                    cpw_status=cpw_status,
                )
            )

        status_rank = {"calculated": 0, "unworn": 1, "missing_price": 2}
        if sort == "cpw_asc":
            items.sort(
                key=lambda x: (
                    status_rank[x.cpw_status],
                    x.cost_per_wear_vnd if x.cost_per_wear_vnd is not None else float("inf"),
                    str(x.item_id),
                )
            )
        elif sort == "cpw_desc":
            items.sort(
                key=lambda x: (
                    status_rank[x.cpw_status],
                    -(x.cost_per_wear_vnd if x.cost_per_wear_vnd is not None else -1.0),
                    str(x.item_id),
                )
            )
        elif sort == "wears_desc":
            items.sort(key=lambda x: (-x.wear_days_count, str(x.item_id)))
        else:
            items.sort(key=lambda x: (x.wear_days_count, str(x.item_id)))

        start_idx = 0
        if cursor:
            for idx, entry in enumerate(items):
                if str(entry.item_id) == cursor:
                    start_idx = idx + 1
                    break
        sliced = items[start_idx : start_idx + limit]
        has_more = (start_idx + limit) < len(items)
        next_cursor = str(sliced[-1].item_id) if has_more and sliced else None
        return PaginatedDataResponse(
            data=sliced,
            meta=PaginatedMeta(
                next_cursor=next_cursor, has_more=has_more, total=len(items)
            ),
        )

