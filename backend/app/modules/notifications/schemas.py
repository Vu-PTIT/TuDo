from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: UUID
    type: Literal["data_export_ready", "data_export_failed"]
    title: str
    body: str
    target_type: Literal["settings_privacy", "data_export"]
    target_id: UUID | None = None
    target_route: str
    read_at: datetime | None = None
    created_at: datetime


class UnreadCountResponse(BaseModel):
    unread_count: int


class MarkAllReadResponse(BaseModel):
    updated_count: int
    cutoff: datetime

