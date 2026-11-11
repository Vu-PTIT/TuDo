from fastapi import status

from app.core.errors import AppError
from app.infrastructure.supabase.client import TransactionalStore
from app.modules.auth.schemas import AuthenticatedUser
from app.modules.settings.repository import SettingsRepository
from app.modules.settings.schemas import UpdateSettingsRequest, UserSettingsResponse


class SettingsService:
    def __init__(self, store: TransactionalStore) -> None:
        self._repo = SettingsRepository(store)

    def get_settings(self, user: AuthenticatedUser) -> UserSettingsResponse:
        row = self._repo.get_settings(user.id)
        return UserSettingsResponse(**row)

    def update_settings(
        self, user: AuthenticatedUser, payload: UpdateSettingsRequest
    ) -> UserSettingsResponse:
        if (
            payload.planner_default_view is None
            and payload.activity_notifications is None
            and payload.analytics_opt_in is None
        ):
            raise AppError(
                code="VALIDATION_ERROR",
                message="Cần cung cấp ít nhất một tùy chọn cài đặt cần thay đổi.",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        row = self._repo.update_settings(
            user_id=user.id,
            expected_version=payload.expected_version,
            planner_default_view=payload.planner_default_view,
            activity_notifications=payload.activity_notifications,
            analytics_opt_in=payload.analytics_opt_in,
        )
        return UserSettingsResponse(**row)

