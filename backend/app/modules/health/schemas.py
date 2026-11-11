from typing import Literal

from pydantic import BaseModel


class PolicyVersionsInfo(BaseModel):
    terms_version: str
    privacy_version: str
    ai_policy_version: str
    analytics_policy_version: str


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    version: str
    native_image_core_loaded: bool
    policy_versions: PolicyVersionsInfo

