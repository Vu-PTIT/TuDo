from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class CreateImageJobRequest(BaseModel):
    asset_id: UUID
    request_key: str = Field(..., min_length=1, max_length=128)


class ImageJobResponse(BaseModel):
    id: UUID
    asset_id: UUID
    request_key: str
    status: Literal["processing", "succeeded", "failed"]
    error_code: str | None = None
    started_at: datetime
    finished_at: datetime | None = None

