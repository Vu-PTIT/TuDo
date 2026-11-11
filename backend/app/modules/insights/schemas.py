from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class InsightsSummaryResponse(BaseModel):
    active_items_count: int
    active_outfits_count: int
    total_wear_count: int


class CostPerWearItemResponse(BaseModel):
    item_id: UUID
    name: str
    category: str
    source: str
    asset_id: UUID | None = None
    image_variant: str | None = None
    availability: str
    purchase_price_vnd: int | None = None
    wear_days_count: int
    cost_per_wear_vnd: float | None = None
    display_cost_per_wear_vnd: int | None = None
    cpw_status: Literal["calculated", "unworn", "missing_price"]

