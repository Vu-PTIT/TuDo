from typing import Annotated

from fastapi import Depends, Header, status

from app.core.errors import AppError
from app.infrastructure.supabase.client import TransactionalStore, get_store
from app.modules.auth.schemas import AuthenticatedUser
from app.modules.auth.service import AuthService


def get_auth_service(
    store: Annotated[TransactionalStore, Depends(get_store)],
) -> AuthService:
    return AuthService(store)


def get_current_user(
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
    auth_service: Annotated[AuthService, Depends(get_auth_service)] = None,  # type: ignore[assignment]
) -> AuthenticatedUser:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise AppError(
            code="UNAUTHENTICATED",
            message="Thiếu hoặc sai định dạng Authorization Bearer token.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    token = authorization[7:].strip()
    return auth_service.verify_bearer_token(token)


def get_active_user(
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    store: Annotated[TransactionalStore, Depends(get_store)],
) -> AuthenticatedUser:
    store.require_active_account(user.id)
    return user

