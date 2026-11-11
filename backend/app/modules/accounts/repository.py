from copy import deepcopy
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from fastapi import status

from app.core.errors import AppError
from app.infrastructure.supabase.client import TransactionalStore, utc_now


class AccountsRepository:
    def __init__(self, store: TransactionalStore) -> None:
        self._store = store

    def get_profile(self, user_id: UUID) -> dict[str, Any] | None:
        with self._store.lock:
            prof = self._store.profiles.get(user_id)
            return deepcopy(prof) if prof else None

    def bootstrap_account(
        self,
        user_id: UUID,
        terms_version: str,
        privacy_version: str,
        display_name: str,
        timezone: str,
    ) -> tuple[bool, dict[str, Any]]:
        with self._store.lock:
            self._store.require_active_account(user_id)
            existing = self._store.profiles.get(user_id)
            if existing is not None:
                return False, deepcopy(existing)

            now = utc_now()
            profile = {
                "id": user_id,
                "display_name": display_name,
                "timezone": timezone,
                "onboarding_completed_at": None,
                "onboarding_skipped_at": None,
                "version": 1,
                "created_at": now,
                "updated_at": now,
            }
            self._store.profiles[user_id] = profile
            self._store.user_settings[user_id] = {
                "owner_id": user_id,
                "planner_default_view": "week",
                "activity_notifications": True,
                "analytics_opt_in": False,
                "version": 1,
                "created_at": now,
                "updated_at": now,
            }
            self._store.account_consents.append(
                {
                    "id": uuid4(),
                    "owner_id": user_id,
                    "kind": "terms",
                    "policy_version": terms_version,
                    "action": "accepted",
                    "revision": 1,
                    "request_key": f"bootstrap:terms:{user_id}",
                    "created_at": now,
                }
            )
            self._store.account_consents.append(
                {
                    "id": uuid4(),
                    "owner_id": user_id,
                    "kind": "privacy",
                    "policy_version": privacy_version,
                    "action": "acknowledged",
                    "revision": 1,
                    "request_key": f"bootstrap:privacy:{user_id}",
                    "created_at": now,
                }
            )
            return True, deepcopy(profile)

    def update_profile(
        self,
        user_id: UUID,
        expected_version: int,
        display_name: str | None,
        timezone: str | None,
    ) -> dict[str, Any]:
        with self._store.lock:
            self._store.require_active_account(user_id)
            prof = self._store.profiles.get(user_id)
            if prof is None:
                raise AppError(
                    code="PROFILE_NOT_READY",
                    message="Hồ sơ chưa được khởi tạo.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            if prof["version"] != expected_version:
                raise AppError(
                    code="CONFLICT",
                    message="Hồ sơ đã được cập nhật từ thiết bị hoặc tab khác. Vui lòng tải lại.",
                    status_code=status.HTTP_409_CONFLICT,
                )
            if display_name is not None:
                prof["display_name"] = display_name
            if timezone is not None:
                prof["timezone"] = timezone
            prof["version"] += 1
            prof["updated_at"] = utc_now()
            return deepcopy(prof)

    def set_onboarding(self, user_id: UUID, action: str) -> dict[str, Any]:
        with self._store.lock:
            self._store.require_active_account(user_id)
            prof = self._store.profiles.get(user_id)
            if prof is None:
                raise AppError(
                    code="PROFILE_NOT_READY",
                    message="Hồ sơ chưa được khởi tạo.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            now = utc_now()
            if action == "complete":
                if prof["onboarding_completed_at"] is None:
                    prof["onboarding_completed_at"] = now
                    prof["onboarding_skipped_at"] = None
                    prof["updated_at"] = now
            elif action == "skip":
                if (
                    prof["onboarding_skipped_at"] is None
                    and prof["onboarding_completed_at"] is None
                ):
                    prof["onboarding_skipped_at"] = now
                    prof["updated_at"] = now
            return deepcopy(prof)

    def list_consents(self, user_id: UUID) -> list[dict[str, Any]]:
        with self._store.lock:
            items = [
                deepcopy(c)
                for c in self._store.account_consents
                if c["owner_id"] == user_id
            ]
            items.sort(key=lambda x: (x["created_at"], str(x["id"])), reverse=True)
            return items

    def get_latest_consent(self, user_id: UUID, kind: str) -> dict[str, Any] | None:
        with self._store.lock:
            matching = [
                c
                for c in self._store.account_consents
                if c["owner_id"] == user_id and c["kind"] == kind
            ]
            if not matching:
                return None
            matching.sort(key=lambda x: x["revision"], reverse=True)
            return deepcopy(matching[0])

    def record_consent(
        self,
        user_id: UUID,
        kind: str,
        policy_version: str,
        action: str,
        request_key: str,
        expected_revision: int,
    ) -> dict[str, Any]:
        with self._store.lock:
            self._store.require_active_account(user_id)
            if user_id not in self._store.profiles:
                raise AppError(
                    code="PROFILE_NOT_READY",
                    message="Hồ sơ chưa được khởi tạo.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            for c in self._store.account_consents:
                if c["owner_id"] == user_id and c["request_key"] == request_key:
                    return deepcopy(c)

            latest = self.get_latest_consent(user_id, kind)
            current_rev = latest["revision"] if latest else 0
            if current_rev != expected_revision:
                raise AppError(
                    code="CONFLICT",
                    message="Trạng thái chấp thuận đã thay đổi ở phiên khác. Vui lòng tải lại.",
                    status_code=status.HTTP_409_CONFLICT,
                )

            entry = {
                "id": uuid4(),
                "owner_id": user_id,
                "kind": kind,
                "policy_version": policy_version,
                "action": action,
                "revision": current_rev + 1,
                "request_key": request_key,
                "created_at": utc_now(),
            }
            self._store.account_consents.append(entry)
            return deepcopy(entry)

    def get_deletion_request_by_key(
        self, user_id: UUID, request_key: str
    ) -> dict[str, Any] | None:
        with self._store.lock:
            for req in self._store.account_deletion_requests.values():
                if req.get("user_id") == user_id and req.get("request_key") == request_key:
                    return deepcopy(req)
            return None

    def create_deletion_request(
        self, user_id: UUID, request_key: str
    ) -> dict[str, Any]:
        with self._store.lock:
            existing_by_key = self.get_deletion_request_by_key(user_id, request_key)
            if existing_by_key is not None:
                return existing_by_key

            if self._store.is_account_deleting(user_id):
                raise AppError(
                    code="ACCOUNT_DELETION_PENDING",
                    message="Tài khoản đã có yêu cầu xóa đang được xử lý.",
                    status_code=status.HTTP_403_FORBIDDEN,
                )

            now = utc_now()
            req_id = uuid4()
            ref_code = f"DEL-{str(req_id)[:8].upper()}"

            # Build cleanup manifest before any deletion occurs
            wardrobe_prefixes = [f"{user_id}/"]
            export_paths = []
            max_upload_expires_at: datetime | None = None

            for asset in self._store.media_assets.values():
                if asset["owner_id"] == user_id:
                    exp = asset.get("upload_expires_at")
                    if exp and (max_upload_expires_at is None or exp > max_upload_expires_at):
                        max_upload_expires_at = exp

            # Cancel queued exports and record export paths in manifest
            for exp_req in self._store.data_export_requests.values():
                if exp_req["owner_id"] == user_id:
                    if exp_req.get("object_path"):
                        export_paths.append(exp_req["object_path"])
                    if exp_req["status"] == "queued":
                        exp_req["status"] = "cancelled"
                        exp_req["updated_at"] = now

            manifest = {
                "wardrobe_prefixes": wardrobe_prefixes,
                "export_prefixes": [f"{user_id}/"],
                "export_paths": export_paths,
                "max_upload_expires_at": (
                    max_upload_expires_at.isoformat() if max_upload_expires_at else None
                ),
            }

            record = {
                "id": req_id,
                "user_id": user_id,
                "request_key": request_key,
                "reference_code": ref_code,
                "status": "requested",
                "cleanup_manifest": manifest,
                "attempts": 0,
                "available_at": now,
                "lease_token": None,
                "lease_until": None,
                "error_code": None,
                "requested_at": now,
                "updated_at": now,
                "finished_at": None,
            }
            self._store.account_deletion_requests[req_id] = record
            self._store.deletion_tombstone_ledger[user_id] = now
            return deepcopy(record)
