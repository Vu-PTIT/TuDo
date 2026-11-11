from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.errors import DataResponse
from app.infrastructure.supabase.client import TransactionalStore, get_store
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.schemas import AuthenticatedUser
from app.modules.settings.schemas import UpdateSettingsRequest, UserSettingsResponse
from app.modules.settings.service import SettingsService

router = APIRouter(prefix="/settings", tags=["settings"])


def get_settings_service(
    store: Annotated[TransactionalStore, Depends(get_store)],
) -> SettingsService:
    return SettingsService(store)


@router.get("", response_model=DataResponse[UserSettingsResponse])
async def get_my_settings(
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[SettingsService, Depends(get_settings_service)],
) -> DataResponse[UserSettingsResponse]:
    return DataResponse(data=service.get_settings(user))


@router.patch("", response_model=DataResponse[UserSettingsResponse])
async def update_my_settings(
    payload: UpdateSettingsRequest,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[SettingsService, Depends(get_settings_service)],
) -> DataResponse[UserSettingsResponse]:
    return DataResponse(data=service.update_settings(user, payload))

