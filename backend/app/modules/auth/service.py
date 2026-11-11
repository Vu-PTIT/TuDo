from uuid import UUID

from fastapi import status

from app.core.config import get_settings
from app.core.errors import AppError
from app.infrastructure.supabase.client import (
    TransactionalStore,
    create_user_supabase_client,
)
from app.modules.auth.schemas import AuthenticatedUser


class AuthService:
    def __init__(self, store: TransactionalStore) -> None:
        self._store = store

    def verify_bearer_token(self, token: str) -> AuthenticatedUser:
        if not token or not token.strip():
            raise AppError(
                code="UNAUTHENTICATED",
                message="Phiên đăng nhập không hợp lệ hoặc đã hết hạn.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        # Check in-memory store first (for local dev / tests)
        with self._store.lock:
            uid = self._store.tokens.get(token)
            if uid is not None:
                user_rec = self._store.auth_users.get(uid)
                if user_rec is None:
                    raise AppError(
                        code="UNAUTHENTICATED",
                        message="Tài khoản không tồn tại hoặc phiên đã hết hạn.",
                        status_code=status.HTTP_401_UNAUTHORIZED,
                    )
                if user_rec.email_confirmed_at is None:
                    raise AppError(
                        code="EMAIL_NOT_VERIFIED",
                        message="Vui lòng xác minh địa chỉ email trước khi sử dụng ứng dụng.",
                        status_code=status.HTTP_403_FORBIDDEN,
                    )
                return AuthenticatedUser(
                    id=user_rec.id,
                    email=user_rec.email,
                    email_confirmed_at=user_rec.email_confirmed_at,
                    pending_email=user_rec.new_email,
                    access_token=token,
                )

        # Otherwise verify via Supabase Auth get_user(token)
        cfg = get_settings()
        if cfg.supabase_url and cfg.supabase_anon_key:
            try:
                client = create_user_supabase_client(token)
                resp = client.auth.get_user(token)
                supa_user = getattr(resp, "user", None)
                if supa_user is None:
                    raise ValueError("Missing user in Auth response")
                confirmed_at = getattr(supa_user, "email_confirmed_at", None)
                if not confirmed_at:
                    raise AppError(
                        code="EMAIL_NOT_VERIFIED",
                        message="Vui lòng xác minh địa chỉ email trước khi sử dụng ứng dụng.",
                        status_code=status.HTTP_403_FORBIDDEN,
                    )
                return AuthenticatedUser(
                    id=UUID(str(supa_user.id)),
                    email=str(supa_user.email or ""),
                    email_confirmed_at=confirmed_at,
                    pending_email=getattr(supa_user, "new_email", None),
                    access_token=token,
                )
            except AppError:
                raise
            except Exception as exc:
                raise AppError(
                    code="UNAUTHENTICATED",
                    message="Phiên đăng nhập không hợp lệ hoặc đã hết hạn.",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                ) from exc

        raise AppError(
            code="UNAUTHENTICATED",
            message="Phiên đăng nhập không hợp lệ hoặc đã hết hạn.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    def verify_password_ephemeral(
        self, user: AuthenticatedUser, current_password: str
    ) -> None:
        """Re-authenticate using an isolated temporary client without mutating shared sessions or logging password."""
        if not current_password:
            raise AppError(
                code="INVALID_CREDENTIALS",
                message="Mật khẩu hiện tại không đúng.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        with self._store.lock:
            user_rec = self._store.auth_users.get(user.id)
            if user_rec is not None:
                if user_rec.password != current_password:
                    raise AppError(
                        code="INVALID_CREDENTIALS",
                        message="Mật khẩu hiện tại không đúng.",
                        status_code=status.HTTP_401_UNAUTHORIZED,
                    )
                return

        cfg = get_settings()
        if cfg.supabase_url and cfg.supabase_anon_key:
            from supabase import ClientOptions, create_client

            temp_client = create_client(
                cfg.supabase_url,
                cfg.supabase_anon_key,
                options=ClientOptions(persist_session=False, auto_refresh_token=False),
            )
            try:
                auth_res = temp_client.auth.sign_in_with_password(
                    {"email": user.email, "password": current_password}
                )
                verified_user = getattr(auth_res, "user", None)
                if verified_user is None or str(verified_user.id) != str(user.id):
                    raise AppError(
                        code="INVALID_CREDENTIALS",
                        message="Mật khẩu hiện tại không đúng.",
                        status_code=status.HTTP_401_UNAUTHORIZED,
                    )
            except AppError:
                raise
            except Exception as exc:
                raise AppError(
                    code="INVALID_CREDENTIALS",
                    message="Mật khẩu hiện tại không đúng.",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                ) from exc
            finally:
                try:
                    temp_client.auth.sign_out({"scope": "local"})
                except Exception:
                    pass
            return

        raise AppError(
            code="INVALID_CREDENTIALS",
            message="Mật khẩu hiện tại không đúng.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

