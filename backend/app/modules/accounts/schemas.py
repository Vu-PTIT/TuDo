from datetime import datetime
from typing import Literal
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, Field, field_validator


def validate_iana_timezone(tz: str) -> str:
    cleaned = tz.strip()
    if not cleaned:
        raise ValueError("Múi giờ không được để trống.")
    try:
        ZoneInfo(cleaned)
    except (ZoneInfoNotFoundError, KeyError, ValueError) as exc:
        raise ValueError(f"Múi giờ IANA không hợp lệ: {cleaned}") from exc
    return cleaned


class BootstrapAccountRequest(BaseModel):
    terms_version: str = Field(..., min_length=1, max_length=50)
    privacy_version: str = Field(..., min_length=1, max_length=50)
    accept_terms: bool
    acknowledge_privacy: bool
    display_name: str | None = Field(default=None, max_length=50)
    timezone: str | None = Field(default=None, max_length=100)

    @field_validator("display_name")
    @classmethod
    def clean_display_name(cls, v: str | None) -> str | None:
        if v is None:
            return None
        stripped = v.strip()
        if not stripped or len(stripped) > 50:
            raise ValueError("Tên hiển thị phải từ 1 đến 50 ký tự.")
        return stripped

    @field_validator("timezone")
    @classmethod
    def check_tz(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return validate_iana_timezone(v)


class AccountProfileResponse(BaseModel):
    id: UUID
    email: str
    pending_email: str | None = None
    display_name: str
    timezone: str
    onboarding_completed_at: datetime | None = None
    onboarding_skipped_at: datetime | None = None
    account_status: Literal["active", "deleting"]
    version: int
    created_at: datetime
    updated_at: datetime


class UpdateProfileRequest(BaseModel):
    display_name: str | None = Field(default=None)
    timezone: str | None = Field(default=None)
    expected_version: int = Field(..., ge=1)

    @field_validator("display_name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is None:
            return None
        stripped = v.strip()
        if not (1 <= len(stripped) <= 50):
            raise ValueError("Tên hiển thị phải từ 1 đến 50 ký tự.")
        return stripped

    @field_validator("timezone")
    @classmethod
    def validate_tz(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return validate_iana_timezone(v)


class OnboardingActionRequest(BaseModel):
    action: Literal["complete", "skip"]


class DeleteAccountRequest(BaseModel):
    current_password: str = Field(..., min_length=1, max_length=256)
    confirmation: str = Field(..., min_length=1, max_length=50)
    request_key: str = Field(..., min_length=1, max_length=128)


class DeleteAccountReceiptResponse(BaseModel):
    id: UUID
    reference_code: str
    status: Literal["requested", "running", "failed", "completed"]
    requested_at: datetime


class ConsentEventResponse(BaseModel):
    id: UUID
    kind: Literal["terms", "privacy", "ai", "analytics"]
    policy_version: str
    action: Literal["accepted", "acknowledged", "withdrawn"]
    revision: int
    request_key: str
    created_at: datetime


class RecordConsentRequest(BaseModel):
    kind: Literal["terms", "privacy", "ai"]
    policy_version: str = Field(..., min_length=1, max_length=64)
    action: Literal["accepted", "acknowledged", "withdrawn"]
    request_key: str = Field(..., min_length=1, max_length=128)
    expected_revision: int = Field(..., ge=0)

