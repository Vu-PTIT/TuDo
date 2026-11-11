from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class CreateDataExportRequest(BaseModel):
    request_key: str = Field(..., min_length=1, max_length=128)


class DataExportResponse(BaseModel):
    id: UUID
    request_key: str
    status: Literal["queued", "running", "ready", "failed", "expired", "cancelled"]
    snapshot_at: datetime | None = None
    expires_at: datetime | None = None
    error_code: str | None = None
    created_at: datetime
    updated_at: datetime

