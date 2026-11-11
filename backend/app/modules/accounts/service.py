from fastapi import status

from app.core.config import get_settings
from app.core.errors import AppError, PaginatedDataResponse, PaginatedMeta
from app.infrastructure.supabase.client import TransactionalStore
from app.modules.accounts.repository import AccountsRepository
from app.modules.accounts.schemas import (
    AccountProfileResponse,
    BootstrapAccountRequest,
    ConsentEventResponse,
    DeleteAccountReceiptResponse,
    DeleteAccountRequest,
    OnboardingActionRequest,
    RecordConsentRequest,
    UpdateProfileRequest,
)
from app.modules.auth.schemas import AuthenticatedUser
from app.modules.auth.service import AuthService

CONFIRMATION_PHRASE = "XÓA TÀI KHOẢN"


class AccountsService:
    def __init__(self, store: TransactionalStore) -> None:
        self._store = store
        self._repo = AccountsRepository(store)
        self._auth_service = AuthService(store)

    def _to_profile_response(
        self, user: AuthenticatedUser, prof: dict
    ) -> AccountProfileResponse:
        is_deleting = self._store.is_account_deleting(user.id)
        return AccountProfileResponse(
            id=prof["id"],
            email=user.email,
            pending_email=user.pending_email,
            display_name=prof["display_name"],
            timezone=prof["timezone"],
            onboarding_completed_at=prof.get("onboarding_completed_at"),
            onboarding_skipped_at=prof.get("onboarding_skipped_at"),
            account_status="deleting" if is_deleting else "active",
            version=prof["version"],
            created_at=prof["created_at"],
            updated_at=prof["updated_at"],
        )

    def bootstrap(
        self, user: AuthenticatedUser, payload: BootstrapAccountRequest
    ) -> tuple[bool, AccountProfileResponse]:
        cfg = get_settings()
        if (
            not payload.accept_terms
            or not payload.acknowledge_privacy
            or payload.terms_version != cfg.current_terms_version
            or payload.privacy_version != cfg.current_privacy_version
        ):
            raise AppError(
                code="POLICY_ACCEPTANCE_REQUIRED",
                message="Vui lòng chấp nhận Điều khoản sử dụng và Chính sách quyền riêng tư phiên bản hiện hành.",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={
                    "required_terms_version": cfg.current_terms_version,
                    "required_privacy_version": cfg.current_privacy_version,
                },
            )

        created, prof = self._repo.bootstrap_account(
            user_id=user.id,
            terms_version=payload.terms_version,
            privacy_version=payload.privacy_version,
            display_name=payload.display_name or "Bạn",
            timezone=payload.timezone or "Asia/Ho_Chi_Minh",
        )
        return created, self._to_profile_response(user, prof)

    def get_me(self, user: AuthenticatedUser) -> AccountProfileResponse:
        prof = self._repo.get_profile(user.id)
        if prof is None:
            raise AppError(
                code="PROFILE_NOT_READY",
                message="Tài khoản chưa hoàn tất khởi tạo hồ sơ.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return self._to_profile_response(user, prof)

    def update_me(
        self, user: AuthenticatedUser, payload: UpdateProfileRequest
    ) -> AccountProfileResponse:
        if payload.display_name is None and payload.timezone is None:
            raise AppError(
                code="VALIDATION_ERROR",
                message="Cần cung cấp ít nhất một trường cần cập nhật (display_name hoặc timezone).",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        prof = self._repo.update_profile(
            user_id=user.id,
            expected_version=payload.expected_version,
            display_name=payload.display_name,
            timezone=payload.timezone,
        )
        return self._to_profile_response(user, prof)

    def set_onboarding(
        self, user: AuthenticatedUser, payload: OnboardingActionRequest
    ) -> AccountProfileResponse:
        prof = self._repo.set_onboarding(user.id, payload.action)
        return self._to_profile_response(user, prof)

    def list_consents(
        self, user: AuthenticatedUser, cursor: str | None = None, limit: int = 20
    ) -> PaginatedDataResponse[ConsentEventResponse]:
        if self._repo.get_profile(user.id) is None:
            raise AppError(
                code="PROFILE_NOT_READY",
                message="Hồ sơ chưa được khởi tạo.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        all_items = self._repo.list_consents(user.id)
        start_idx = 0
        if cursor:
            for idx, item in enumerate(all_items):
                if str(item["id"]) == cursor:
                    start_idx = idx + 1
                    break
        sliced = all_items[start_idx : start_idx + limit]
        has_more = (start_idx + limit) < len(all_items)
        next_cursor = str(sliced[-1]["id"]) if has_more and sliced else None
        return PaginatedDataResponse(
            data=[ConsentEventResponse(**c) for c in sliced],
            meta=PaginatedMeta(next_cursor=next_cursor, has_more=has_more),
        )

    def record_consent(
        self, user: AuthenticatedUser, payload: RecordConsentRequest
    ) -> ConsentEventResponse:
        cfg = get_settings()
        valid_pairs: dict[str, tuple[str, set[str]]] = {
            "terms": (cfg.current_terms_version, {"accepted"}),
            "privacy": (cfg.current_privacy_version, {"acknowledged"}),
            "ai": (cfg.current_ai_policy_version, {"accepted", "withdrawn"}),
        }
        expected_ver, allowed_actions = valid_pairs[payload.kind]
        if payload.policy_version != expected_ver or payload.action not in allowed_actions:
            raise AppError(
                code="INVALID_CONSENT_VERSION",
                message="Phiên bản chính sách hoặc hành động chấp thuận không hợp lệ.",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"expected_policy_version": expected_ver},
            )

        rec = self._repo.record_consent(
            user_id=user.id,
            kind=payload.kind,
            policy_version=payload.policy_version,
            action=payload.action,
            request_key=payload.request_key,
            expected_revision=payload.expected_revision,
        )
        return ConsentEventResponse(**rec)

    def request_account_deletion(
        self, user: AuthenticatedUser, payload: DeleteAccountRequest
    ) -> DeleteAccountReceiptResponse:
        if payload.confirmation != CONFIRMATION_PHRASE:
            raise AppError(
                code="VALIDATION_ERROR",
                message=f"Chuỗi xác nhận phải chính xác là '{CONFIRMATION_PHRASE}'.",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        # Idempotent replay if already accepted with the exact same request_key
        existing = self._repo.get_deletion_request_by_key(user.id, payload.request_key)
        if existing is not None:
            return DeleteAccountReceiptResponse(**existing)

        if self._store.is_account_deleting(user.id):
            raise AppError(
                code="ACCOUNT_DELETION_PENDING",
                message="Tài khoản đã có yêu cầu xóa đang được xử lý.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        # Verify password via isolated ephemeral Auth check
        self._auth_service.verify_password_ephemeral(user, payload.current_password)

        record = self._repo.create_deletion_request(user.id, payload.request_key)
        return DeleteAccountReceiptResponse(**record)

