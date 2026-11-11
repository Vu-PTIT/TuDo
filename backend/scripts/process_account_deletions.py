from datetime import datetime, timedelta
from uuid import UUID, uuid4

from app.core.config import get_settings
from app.infrastructure.supabase.client import TransactionalStore, get_store, utc_now

LEASE_SECONDS = 120


def process_pending_account_deletions(
    store: TransactionalStore | None = None,
    ignore_upload_expiry_for_test: bool = False,
) -> int:
    """Process durable account deletion requests, cleaning storage prefixes, dependent tables, and redacting PII."""
    target_store = store or get_store()
    cfg = get_settings()
    completed_count = 0

    while True:
        claimed_id: UUID | None = None
        lease_token = uuid4()
        now = utc_now()

        with target_store.lock:
            for req_id, req in target_store.account_deletion_requests.items():
                is_ready = req["status"] in ("requested", "failed") and req["available_at"] <= now
                is_stale_running = (
                    req["status"] == "running"
                    and req.get("lease_until") is not None
                    and req["lease_until"] <= now
                )
                if is_ready or is_stale_running:
                    req["status"] = "running"
                    req["attempts"] += 1
                    req["lease_token"] = lease_token
                    req["lease_until"] = now + timedelta(seconds=LEASE_SECONDS)
                    req["updated_at"] = now
                    claimed_id = req_id
                    break

        if claimed_id is None:
            break

        with target_store.lock:
            req = target_store.account_deletion_requests[claimed_id]
            user_id: UUID | None = req.get("user_id")
            manifest: dict = req.get("cleanup_manifest", {})

        if user_id is None:
            with target_store.lock:
                req["status"] = "completed"
                req["lease_token"] = None
                req["lease_until"] = None
                req["finished_at"] = utc_now()
            completed_count += 1
            continue

        # 1. If any upload grant was issued before deletion request and hasn't expired yet, wait until it expires
        max_upload_exp_str = manifest.get("max_upload_expires_at")
        if max_upload_exp_str and not ignore_upload_expiry_for_test:
            max_upload_exp = datetime.fromisoformat(max_upload_exp_str)
            if max_upload_exp > now:
                with target_store.lock:
                    req = target_store.account_deletion_requests[claimed_id]
                    req["status"] = "requested"
                    req["available_at"] = max_upload_exp
                    req["lease_token"] = None
                    req["lease_until"] = None
                    req["updated_at"] = now
                break

        # 2. Cancel/revoke any export requests or running image jobs for this user
        with target_store.lock:
            for exp_req in target_store.data_export_requests.values():
                if exp_req["owner_id"] == user_id:
                    exp_req["status"] = "cancelled"
                    exp_req["lease_token"] = None
                    exp_req["lease_until"] = None
            for job in target_store.image_jobs.values():
                if job["owner_id"] == user_id and job["status"] == "processing":
                    job["status"] = "failed"
                    job["error_code"] = "ACCOUNT_DELETION_PENDING"
                    job["finished_at"] = now

        # 3. First storage sweep across wardrobe-media and account-exports prefixes
        prefix = f"{user_id}/"
        for path in target_store.list_storage_prefix(cfg.storage_bucket_wardrobe, prefix):
            target_store.delete_storage_object(cfg.storage_bucket_wardrobe, path)
        for path in target_store.list_storage_prefix(cfg.storage_bucket_exports, prefix):
            target_store.delete_storage_object(cfg.storage_bucket_exports, path)
        for extra_path in manifest.get("export_paths", []):
            target_store.delete_storage_object(cfg.storage_bucket_exports, extra_path)

        # 4. Delete all user rows in dependency order and redact operational support audit events
        with target_store.lock:
            for wl_id in [
                k for k, v in target_store.wear_logs.items() if v["owner_id"] == user_id
            ]:
                target_store.wear_logs.pop(wl_id, None)
                target_store.wear_log_items.pop(wl_id, None)

            for pe_id in [
                k for k, v in target_store.planner_entries.items() if v["owner_id"] == user_id
            ]:
                target_store.planner_entries.pop(pe_id, None)

            for o_id in [
                k for k, v in target_store.outfits.items() if v["owner_id"] == user_id
            ]:
                target_store.outfits.pop(o_id, None)
                target_store.outfit_items.pop(o_id, None)

            for wi_id in [
                k for k, v in target_store.wardrobe_items.items() if v["owner_id"] == user_id
            ]:
                target_store.wardrobe_items.pop(wi_id, None)

            for job_id in [
                k for k, v in target_store.image_jobs.items() if v["owner_id"] == user_id
            ]:
                target_store.image_jobs.pop(job_id, None)

            for ma_id in [
                k for k, v in target_store.media_assets.items() if v["owner_id"] == user_id
            ]:
                target_store.media_assets.pop(ma_id, None)

            for n_id in [
                k for k, v in target_store.notifications.items() if v["owner_id"] == user_id
            ]:
                target_store.notifications.pop(n_id, None)

            user_support_ids = {
                k for k, v in target_store.support_requests.items() if v["owner_id"] == user_id
            }
            for sr_id in user_support_ids:
                target_store.support_requests.pop(sr_id, None)

            for audit in target_store.support_audit_events:
                if audit.get("request_id") in user_support_ids:
                    audit["request_id"] = None
                    audit["action"] = "redacted_on_account_delete"

            for de_id in [
                k
                for k, v in target_store.data_export_requests.items()
                if v["owner_id"] == user_id
            ]:
                target_store.data_export_requests.pop(de_id, None)

            target_store.account_consents = [
                c for c in target_store.account_consents if c["owner_id"] != user_id
            ]
            target_store.user_settings.pop(user_id, None)
            target_store.profiles.pop(user_id, None)

            # Remove Auth user and revoke tokens
            target_store.auth_users.pop(user_id, None)
            for tok in [t for t, uid in target_store.tokens.items() if uid == user_id]:
                target_store.tokens.pop(tok, None)

        # 5. Final storage sweep to eliminate any late-written objects
        for path in target_store.list_storage_prefix(cfg.storage_bucket_wardrobe, prefix):
            target_store.delete_storage_object(cfg.storage_bucket_wardrobe, path)
        for path in target_store.list_storage_prefix(cfg.storage_bucket_exports, prefix):
            target_store.delete_storage_object(cfg.storage_bucket_exports, path)

        # 6. Mark deletion request completed and strip user_id & manifest per minimal retention policy
        with target_store.lock:
            req = target_store.account_deletion_requests[claimed_id]
            finish_now = utc_now()
            req["user_id"] = None
            req["cleanup_manifest"] = {}
            req["status"] = "completed"
            req["lease_token"] = None
            req["lease_until"] = None
            req["updated_at"] = finish_now
            req["finished_at"] = finish_now
            completed_count += 1

    return completed_count


if __name__ == "__main__":
    count = process_pending_account_deletions()
    print(f"Completed {count} account deletion request(s).")

