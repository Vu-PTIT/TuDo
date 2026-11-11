from copy import deepcopy
from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import RLock
from typing import Any
from uuid import UUID

from fastapi import status

from app.core.config import get_settings
from app.core.errors import AppError

try:
    from supabase import Client, ClientOptions, create_client
except ImportError:
    Client = Any  # type: ignore[misc,assignment]
    ClientOptions = Any  # type: ignore[misc,assignment]
    create_client = None


def utc_now() -> datetime:
    return datetime.now(UTC)


def create_user_supabase_client(access_token: str) -> Client:
    """Create a request-scoped Supabase client bound to the caller's JWT (never shared across users)."""
    cfg = get_settings()
    if not cfg.supabase_url or not cfg.supabase_anon_key or create_client is None:
        raise AppError(
            code="SERVICE_UNAVAILABLE",
            message="Supabase client is not configured.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    options = ClientOptions(
        headers={"Authorization": f"Bearer {access_token}"},
        persist_session=False,
        auto_refresh_token=False,
    )
    return create_client(cfg.supabase_url, cfg.supabase_anon_key, options=options)


def create_service_supabase_client() -> Client:
    """Create a narrow server-only Supabase client for privileged tasks (media finalize, deletion, exports)."""
    cfg = get_settings()
    if not cfg.supabase_url or not cfg.supabase_service_role_key or create_client is None:
        raise AppError(
            code="SERVICE_UNAVAILABLE",
            message="Supabase service client is not configured.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    options = ClientOptions(persist_session=False, auto_refresh_token=False)
    return create_client(cfg.supabase_url, cfg.supabase_service_role_key, options=options)


@dataclass
class AuthUserRecord:
    id: UUID
    email: str
    email_confirmed_at: datetime | None = field(default_factory=utc_now)
    new_email: str | None = None
    password: str = "ValidPassword123!"


class TransactionalStore:
    """Thread-safe store enforcing RLS, RPC transaction rules, versions, and private storage buckets."""

    def __init__(self) -> None:
        self.lock = RLock()
        self.auth_users: dict[UUID, AuthUserRecord] = {}
        self.tokens: dict[str, UUID] = {}
        self.profiles: dict[UUID, dict[str, Any]] = {}
        self.user_settings: dict[UUID, dict[str, Any]] = {}
        self.account_consents: list[dict[str, Any]] = []
        self.data_export_requests: dict[UUID, dict[str, Any]] = {}
        self.account_deletion_requests: dict[UUID, dict[str, Any]] = {}
        self.deletion_tombstone_ledger: dict[UUID, datetime] = {}
        self.notifications: dict[UUID, dict[str, Any]] = {}
        self.support_requests: dict[UUID, dict[str, Any]] = {}
        self.support_audit_events: list[dict[str, Any]] = []
        self.media_assets: dict[UUID, dict[str, Any]] = {}
        self.wardrobe_items: dict[UUID, dict[str, Any]] = {}
        self.outfits: dict[UUID, dict[str, Any]] = {}
        self.outfit_items: dict[UUID, list[dict[str, Any]]] = {}
        self.planner_entries: dict[UUID, dict[str, Any]] = {}
        self.wear_logs: dict[UUID, dict[str, Any]] = {}
        self.wear_log_items: dict[UUID, list[dict[str, Any]]] = {}
        self.image_jobs: dict[UUID, dict[str, Any]] = {}
        # Storage buckets -> object_path -> bytes
        self.storage_objects: dict[str, dict[str, bytes]] = {
            "wardrobe-media": {},
            "account-exports": {},
        }

    def is_account_deleting(self, user_id: UUID) -> bool:
        with self.lock:
            for req in self.account_deletion_requests.values():
                if req.get("user_id") == user_id and req.get("status") in (
                    "requested",
                    "running",
                    "failed",
                ):
                    return True
            return user_id in self.deletion_tombstone_ledger

    def require_active_account(self, user_id: UUID) -> None:
        if self.is_account_deleting(user_id):
            raise AppError(
                code="ACCOUNT_DELETION_PENDING",
                message="Tài khoản đang trong quá trình xóa dữ liệu, không thể thực hiện thao tác mới.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

    def put_storage_object(self, bucket: str, path: str, data: bytes) -> None:
        with self.lock:
            self.storage_objects.setdefault(bucket, {})[path] = bytes(data)

    def get_storage_object(self, bucket: str, path: str) -> bytes | None:
        with self.lock:
            return self.storage_objects.get(bucket, {}).get(path)

    def delete_storage_object(self, bucket: str, path: str) -> bool:
        with self.lock:
            bucket_map = self.storage_objects.get(bucket, {})
            if path in bucket_map:
                del bucket_map[path]
                return True
            return False

    def list_storage_prefix(self, bucket: str, prefix: str) -> list[str]:
        with self.lock:
            bucket_map = self.storage_objects.get(bucket, {})
            return [k for k in bucket_map if k.startswith(prefix)]

    def snapshot_for_user(self, user_id: UUID) -> dict[str, Any]:
        """Take an atomic REPEATABLE READ equivalent snapshot of all user data for JSON export."""
        with self.lock:
            snapshot_at = utc_now()
            profile = deepcopy(self.profiles.get(user_id))
            settings = deepcopy(self.user_settings.get(user_id))
            consents = [
                deepcopy(c) for c in self.account_consents if c["owner_id"] == user_id
            ]
            items = [
                deepcopy(i) for i in self.wardrobe_items.values() if i["owner_id"] == user_id
            ]
            assets = [
                deepcopy(a) for a in self.media_assets.values() if a["owner_id"] == user_id
            ]
            outfits = []
            for o in self.outfits.values():
                if o["owner_id"] == user_id:
                    o_copy = deepcopy(o)
                    o_copy["items"] = deepcopy(self.outfit_items.get(o["id"], []))
                    outfits.append(o_copy)
            entries = [
                deepcopy(e) for e in self.planner_entries.values() if e["owner_id"] == user_id
            ]
            logs = []
            for wl in self.wear_logs.values():
                if wl["owner_id"] == user_id:
                    wl_copy = deepcopy(wl)
                    wl_copy["items"] = deepcopy(self.wear_log_items.get(wl["id"], []))
                    logs.append(wl_copy)
            notifs = [
                deepcopy(n) for n in self.notifications.values() if n["owner_id"] == user_id
            ]
            supports = [
                deepcopy(s) for s in self.support_requests.values() if s["owner_id"] == user_id
            ]
            return {
                "snapshot_at": snapshot_at,
                "profile": profile,
                "settings": settings,
                "consents": consents,
                "wardrobe_items": items,
                "media_assets": assets,
                "outfits": outfits,
                "planner_entries": entries,
                "wear_logs": logs,
                "notifications": notifs,
                "support_requests": supports,
            }


_default_store = TransactionalStore()


def get_store() -> TransactionalStore:
    return _default_store
