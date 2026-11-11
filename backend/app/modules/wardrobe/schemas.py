from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

ItemCategory = Literal[
    "top",
    "bottom",
    "dress",
    "skirt",
    "outerwear",
    "shoes",
    "bag",
    "accessory",
    "other",
]

ItemAvailability = Literal["available", "laundry", "unavailable", "archived"]
ItemSource = Literal["photo", "placeholder"]
ImageVariant = Literal["original", "cutout"]


class CreateWardrobeItemRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: ItemCategory
    source: ItemSource = "photo"
    asset_id: UUID | None = None
    image_variant: ImageVariant | None = None
    back_asset_id: UUID | None = None
    back_image_variant: ImageVariant | None = None
    colors: list[str] = Field(default_factory=list, max_length=10)
    size: str | None = Field(default=None, max_length=50)
    brand: str | None = Field(default=None, max_length=100)
    purchase_price_vnd: int | None = Field(default=None, ge=0)
    purchase_date: date | None = None
    notes: str | None = Field(default=None, max_length=1000)
    availability: ItemAvailability = "available"

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        s = v.strip()
        if not (1 <= len(s) <= 100):
            raise ValueError("Tên món đồ phải từ 1 đến 100 ký tự.")
        return s

    @model_validator(mode="after")
    def check_source_asset(self) -> "CreateWardrobeItemRequest":
        if self.source == "photo" and (self.asset_id is None or self.image_variant is None):
            raise ValueError(
                "Món đồ tạo từ ảnh (source='photo') bắt buộc có asset_id và image_variant."
            )
        if self.source == "placeholder" and (
            self.back_asset_id is not None or self.back_image_variant is not None
        ):
            raise ValueError(
                "Món đồ dạng thẻ tạm (source='placeholder') không được gắn ảnh mặt sau."
            )
        if (self.back_asset_id is None) != (self.back_image_variant is None):
            raise ValueError(
                "Ảnh mặt sau (back_asset_id) và phiên bản ảnh mặt sau (back_image_variant) phải được cung cấp cùng nhau."
            )
        return self


class UpdateWardrobeItemRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    category: ItemCategory | None = None
    source: ItemSource | None = None
    asset_id: UUID | None = None
    image_variant: ImageVariant | None = None
    back_asset_id: UUID | None = None
    back_image_variant: ImageVariant | None = None
    clear_back_image: bool = False
    colors: list[str] | None = Field(default=None, max_length=10)
    size: str | None = Field(default=None, max_length=50)
    brand: str | None = Field(default=None, max_length=100)
    purchase_price_vnd: int | None = Field(default=None, ge=0)
    clear_purchase_price: bool = False
    purchase_date: date | None = None
    notes: str | None = Field(default=None, max_length=1000)
    availability: ItemAvailability | None = None

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip()
        if not (1 <= len(s) <= 100):
            raise ValueError("Tên món đồ phải từ 1 đến 100 ký tự.")
        return s


class WardrobeItemResponse(BaseModel):
    id: UUID
    name: str
    category: ItemCategory
    source: ItemSource
    asset_id: UUID | None = None
    image_variant: ImageVariant | None = None
    back_asset_id: UUID | None = None
    back_image_variant: ImageVariant | None = None
    has_back_image: bool = False
    colors: list[str]
    size: str | None = None
    brand: str | None = None
    purchase_price_vnd: int | None = None
    purchase_date: date | None = None
    notes: str | None = None
    availability: ItemAvailability
    wear_days_count: int = 0
    cost_per_wear_vnd: float | None = None
    display_cost_per_wear_vnd: int | None = None
    cpw_status: Literal["calculated", "unworn", "missing_price"] = "missing_price"
    created_at: datetime
    updated_at: datetime

