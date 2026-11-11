from fastapi import APIRouter

from app.core.config import get_settings
from app.core.errors import DataResponse
from app.infrastructure.native.image_core import is_native_available
from app.modules.health.schemas import HealthResponse, PolicyVersionsInfo

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=DataResponse[HealthResponse])
async def get_health() -> DataResponse[HealthResponse]:
    cfg = get_settings()
    native_ok = is_native_available()
    return DataResponse(
        data=HealthResponse(
            status="ok" if native_ok else "degraded",
            version=cfg.app_version,
            native_image_core_loaded=native_ok,
            policy_versions=PolicyVersionsInfo(
                terms_version=cfg.current_terms_version,
                privacy_version=cfg.current_privacy_version,
                ai_policy_version=cfg.current_ai_policy_version,
                analytics_policy_version=cfg.current_analytics_policy_version,
            ),
        )
    )

