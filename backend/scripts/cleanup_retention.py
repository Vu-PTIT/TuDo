from datetime import timedelta

from app.core.config import get_settings
from app.infrastructure.supabase.client import TransactionalStore, get_store, utc_now

EXPORT_RECORD_RETENTION_DAYS = 30
NOTIFICATION_RETENTION_DAYS = 90
SUPPORT_CLOSED_RETENTION_DAYS = 90


def run_retention_cleanup(store: TransactionalStore | None = None) -> dict[str, int]:
    """Clean expired data export files, old notifications (90d), and closed support tickets (90d after close)."""
    target_store = store or get_store()
    cfg = get_settings()
    now = utc_now()

    expired_export_files = 0
    pruned_export_records = 0
    pruned_notifications = 0
    pruned_support_requests = 0

    with target_store.lock:
        # 1. Expire ready data exports past expires_at and delete their storage objects
        for export_id, req in list(target_store.data_export_requests.items()):
            if (
                req["status"] == "ready"
                and req.get("expires_at") is not None
                and req["expires_at"] <= now
            ):
                if req.get("object_path"):
                    target_store.delete_storage_object(
                        cfg.storage_bucket_exports, req["object_path"]
                    )
                    req["object_path"] = None
                req["status"] = "expired"
                req["updated_at"] = now
                expired_export_files += 1

            if (
                req["status"] in ("expired", "cancelled", "failed")
                and req["updated_at"] <= now - timedelta(days=EXPORT_RECORD_RETENTION_DAYS)
            ):
                target_store.data_export_requests.pop(export_id, None)
                pruned_export_records += 1

        # 2. Prune notifications older than 90 days
        notif_cutoff = now - timedelta(days=NOTIFICATION_RETENTION_DAYS)
        for n_id, notif in list(target_store.notifications.items()):
            if notif["created_at"] <= notif_cutoff:
                target_store.notifications.pop(n_id, None)
                pruned_notifications += 1

        # 3. Prune closed support requests older than 90 days after closed_at (never auto-close open tickets!)
        support_cutoff = now - timedelta(days=SUPPORT_CLOSED_RETENTION_DAYS)
        for sr_id, sr in list(target_store.support_requests.items()):
            if (
                sr["status"] == "closed"
                and sr.get("closed_at") is not None
                and sr["closed_at"] <= support_cutoff
            ):
                target_store.support_requests.pop(sr_id, None)
                pruned_support_requests += 1

    return {
        "expired_export_files": expired_export_files,
        "pruned_export_records": pruned_export_records,
        "pruned_notifications": pruned_notifications,
        "pruned_support_requests": pruned_support_requests,
    }


if __name__ == "__main__":
    result = run_retention_cleanup()
    print(f"Retention cleanup complete: {result}")

