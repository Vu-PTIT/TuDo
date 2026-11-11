from datetime import date, datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class SnapshotItemSchema(BaseModel):
    item_id: UUID
    name: str
    category: str
    source: str
    asset_id: UUID | None = None
    image_variant: str | None = None
    variant_metadata: dict[str, Any] | None = None
    back_asset_id: UUID | None = None
    back_image_variant: str | None = None
    back_variant_metadata: dict[str, Any] | None = None
    display_side: Literal["front", "back"] = "front"
    x: float
    y: float
    w: float
    h: float
    z_index: int


class OutfitSnapshotSchema(BaseModel):
    schema_version: int = 1
    outfit_id: UUID
    outfit_name: str
    items: list[SnapshotItemSchema]


class LiveItemWarningSchema(BaseModel):
    item_id: UUID
    item_name: str
    issue: Literal["laundry", "unavailable", "archived", "deleted"]


class CreatePlannerEntryRequest(BaseModel):
    outfit_id: UUID
    scheduled_date: date
    event_label: str | None = Field(default=None, max_length=100)

    @field_validator("event_label")
    @classmethod
    def clean_label(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip()
        return s if s else None


class UpdatePlannerEntryRequest(BaseModel):
    outfit_id: UUID | None = None
    scheduled_date: date | None = None
    event_label: str | None = Field(default=None, max_length=100)
    clear_event_label: bool = False
    expected_version: int = Field(..., ge=1)

    @field_validator("event_label")
    @classmethod
    def clean_label(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip()
        return s if s else None


class WearOperationRequest(BaseModel):
    operation_key: str = Field(..., min_length=1, max_length=128)
    expected_version: int = Field(..., ge=1)


class SkipPlannerEntryRequest(BaseModel):
    expected_version: int = Field(..., ge=1)
    operation_key: str | None = Field(default=None, max_length=128)


class PlannerEntryResponse(BaseModel):
    id: UUID
    outfit_id: UUID | None = None
    scheduled_date: date
    event_label: str | None = None
    status: Literal["planned", "worn", "skipped"]
    outfit_snapshot: OutfitSnapshotSchema
    live_warnings: list[LiveItemWarningSchema] = Field(default_factory=list)
    version: int
    last_operation_key: str | None = None
    created_at: datetime
    updated_at: datetime

