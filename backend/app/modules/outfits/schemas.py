from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

GarmentSide = Literal["front", "back"]


class OutfitCanvasItemInput(BaseModel):
    item_id: UUID
    x: float = Field(..., ge=0.0, le=1.0)
    y: float = Field(..., ge=0.0, le=1.0)
    w: float = Field(..., gt=0.0, le=1.0)
    h: float = Field(..., gt=0.0, le=1.0)
    z_index: int = Field(default=0, ge=0)
    display_side: GarmentSide = "front"

    @model_validator(mode="after")
    def validate_bounds(self) -> "OutfitCanvasItemInput":
        if self.x + self.w > 1.000001 or self.y + self.h > 1.000001:
            raise ValueError(
                "Tọa độ và kích thước món đồ vượt ngoài khung bảng phối (x + w <= 1, y + h <= 1)."
            )
        return self


class CreateOutfitRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    notes: str | None = Field(default=None, max_length=1000)
    style_tags: list[str] = Field(default_factory=list, max_length=10)
    occasion_tags: list[str] = Field(default_factory=list, max_length=10)
    items: list[OutfitCanvasItemInput] = Field(..., min_length=1, max_length=12)

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        s = v.strip()
        if not (1 <= len(s) <= 100):
            raise ValueError("Tên outfit phải từ 1 đến 100 ký tự.")
        return s

    @model_validator(mode="after")
    def validate_unique_items(self) -> "CreateOutfitRequest":
        seen: set[UUID] = set()
        for item in self.items:
            if item.item_id in seen:
                raise ValueError("Một món đồ không được xuất hiện trùng lặp trong cùng một outfit.")
            seen.add(item.item_id)
        return self


class UpdateOutfitRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    notes: str | None = Field(default=None, max_length=1000)
    style_tags: list[str] | None = Field(default=None, max_length=10)
    occasion_tags: list[str] | None = Field(default=None, max_length=10)
    items: list[OutfitCanvasItemInput] | None = Field(default=None, min_length=1, max_length=12)
    expected_version: int = Field(..., ge=1)

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip()
        if not (1 <= len(s) <= 100):
            raise ValueError("Tên outfit phải từ 1 đến 100 ký tự.")
        return s

    @model_validator(mode="after")
    def validate_unique_items(self) -> "UpdateOutfitRequest":
        if self.items is not None:
            seen: set[UUID] = set()
            for item in self.items:
                if item.item_id in seen:
                    raise ValueError(
                        "Một món đồ không được xuất hiện trùng lặp trong cùng một outfit."
                    )
                seen.add(item.item_id)
        return self


class OutfitItemDetailResponse(BaseModel):
    item_id: UUID
    x: float
    y: float
    w: float
    h: float
    z_index: int
    display_side: GarmentSide = "front"
    item_name: str | None = None
    category: str | None = None
    source: str | None = None
    asset_id: UUID | None = None
    image_variant: str | None = None
    back_asset_id: UUID | None = None
    back_image_variant: str | None = None
    availability: str | None = None
    item_state: Literal["ready", "laundry", "unavailable", "archived", "deleted"] = "ready"


class OutfitResponse(BaseModel):
    id: UUID
    name: str
    notes: str | None = None
    style_tags: list[str]
    occasion_tags: list[str]
    version: int
    items: list[OutfitItemDetailResponse]
    has_missing_or_unavailable_items: bool = False
    created_at: datetime
    updated_at: datetime

