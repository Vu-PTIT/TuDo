from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

SupportCategory = Literal[
    "account",
    "media_ai",
    "wardrobe",
    "outfit_planner",
    "privacy_data",
    "bug",
    "feedback",
]


class SupportDiagnosticsSchema(BaseModel):
    """Strict whitelist schema for support diagnostics (rejects any unknown/sensitive fields)."""

    model_config = ConfigDict(extra="forbid")

    request_id: str | None = Field(default=None, max_length=128)
    error_code: str | None = Field(default=None, max_length=100)
    app_version: str | None = Field(default=None, max_length=64)
    browser_family: str | None = Field(default=None, max_length=100)


class CreateSupportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_key: str = Field(..., min_length=1, max_length=128)
    category: SupportCategory
    subject: str = Field(..., min_length=5, max_length=120)
    description: str = Field(..., min_length=20, max_length=4000)
    diagnostics: SupportDiagnosticsSchema | None = None

    @field_validator("subject")
    @classmethod
    def clean_subject(cls, v: str) -> str:
        s = v.strip()
        if not (5 <= len(s) <= 120):
            raise ValueError("Tiêu đề phải từ 5 đến 120 ký tự.")
        return s

    @field_validator("description")
    @classmethod
    def clean_description(cls, v: str) -> str:
        s = v.strip()
        if not (20 <= len(s) <= 4000):
            raise ValueError("Mô tả phải từ 20 đến 4000 ký tự.")
        return s


class SupportRequestResponse(BaseModel):
    id: UUID
    reference_code: str
    request_key: str
    category: SupportCategory
    subject: str
    description: str
    diagnostics: SupportDiagnosticsSchema | None = None
    status: Literal["received", "in_review", "closed"]
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None = None

