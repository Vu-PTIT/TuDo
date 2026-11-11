from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class UserSettingsResponse(BaseModel):
    planner_default_view: Literal["week", "month"]
    activity_notifications: bool
    analytics_opt_in: bool
    version: int
    updated_at: datetime


class UpdateSettingsRequest(BaseModel):
    planner_default_view: Literal["week", "month"] | None = None
    activity_notifications: bool | None = None
    analytics_opt_in: bool | None = None
    expected_version: int = Field(..., ge=1)

