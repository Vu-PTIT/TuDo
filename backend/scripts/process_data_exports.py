import json
from datetime import timedelta
from typing import Any
from uuid import UUID, uuid4

from app.core.config import get_settings
from app.infrastructure.supabase.client import TransactionalStore, get_store, utc_now
from app.modules.notifications.repository import NotificationsRepository

MAX_EXPORT_ATTEMPTS = 3
LEASE_SECONDS = 120


def _serialize_value(val: Any) -> Any:
    if isinstance(val, UUID):
        return str(val)
    if hasattr(val, "isoformat"):
        return val.isoformat()
    if isinstance(val, dict):
        return {k: _serialize_value(v) for k, v in val.items()}
    if isinstance(val, list):
        return [_serialize_value(v) for v in val]
    return val


def build_whitelisted_export_payload(raw_snapshot: dict[str, Any]) -> dict[str, Any]:
    """Build user-facing JSON export without internal paths, signed URLs, tokens, or secrets."""
    profile = raw_snapshot.get("profile")
    clean_profile = (
        {
            "id": profile["id"],
            "display_name": profile["display_name"],
            "timezone": profile["timezone"],
            "onboarding_completed_at": profile.get("onboarding_completed_at"),
            "onboarding_skipped_at": profile.get("onboarding_skipped_at"),
            "created_at": profile["created_at"],
            "updated_at": profile["updated_at"],
        }
        if profile
        else None
    )

    settings = raw_snapshot.get("settings")
    clean_settings = (
        {
            "planner_default_view": settings["planner_default_view"],
            "activity_notifications": settings["activity_notifications"],
            "analytics_opt_in": settings["analytics_opt_in"],
            "updated_at": settings["updated_at"],
        }
        if settings
        else None
    )

    clean_consents = [
        {
            "id": c["id"],
            "kind": c["kind"],
            "policy_version": c["policy_version"],
            "action": c["action"],
            "revision": c["revision"],
            "created_at": c["created_at"],
        }
        for c in raw_snapshot.get("consents", [])
    ]

    clean_assets = []
    for a in raw_snapshot.get("media_assets", []):
        variants_clean = {}
        for v_key, v_meta in a.get("variant_metadata", {}).items():
            variants_clean[v_key] = {
                "width": v_meta.get("width"),
                "height": v_meta.get("height"),
                "format": v_meta.get("format"),
                "has_alpha": v_meta.get("has_alpha"),
            }
        clean_assets.append(
            {
                "id": a["id"],
                "status": a["status"],
                "variants": variants_clean,
                "created_at": a["created_at"],
            }
        )

    clean_items = [
        {
            "id": i["id"],
            "name": i["name"],
            "category": i["category"],
            "source": i["source"],
            "asset_id": i.get("asset_id"),
            "image_variant": i.get("image_variant"),
            "colors": i.get("colors", []),
            "size": i.get("size"),
            "brand": i.get("brand"),
            "purchase_price_vnd": i.get("purchase_price_vnd"),
            "purchase_date": i.get("purchase_date"),
            "notes": i.get("notes"),
            "availability": i["availability"],
            "deleted_at": i.get("deleted_at"),
            "created_at": i["created_at"],
            "updated_at": i["updated_at"],
        }
        for i in raw_snapshot.get("wardrobe_items", [])
    ]

    clean_outfits = [
        {
            "id": o["id"],
            "name": o["name"],
            "notes": o.get("notes"),
            "style_tags": o.get("style_tags", []),
            "occasion_tags": o.get("occasion_tags", []),
            "deleted_at": o.get("deleted_at"),
            "items": [
                {
                    "item_id": oi["item_id"],
                    "x": oi["x"],
                    "y": oi["y"],
                    "w": oi["w"],
                    "h": oi["h"],
                    "z_index": oi["z_index"],
                }
                for oi in o.get("items", [])
            ],
            "created_at": o["created_at"],
            "updated_at": o["updated_at"],
        }
        for o in raw_snapshot.get("outfits", [])
    ]

    clean_entries = []
    for e in raw_snapshot.get("planner_entries", []):
        snap = e.get("outfit_snapshot", {})
        clean_snap_items = [
            {
                "item_id": si["item_id"],
                "name": si["name"],
                "category": si["category"],
                "source": si["source"],
                "asset_id": si.get("asset_id"),
                "image_variant": si.get("image_variant"),
                "x": si["x"],
                "y": si["y"],
                "w": si["w"],
                "h": si["h"],
                "z_index": si["z_index"],
            }
            for si in snap.get("items", [])
        ]
        clean_entries.append(
            {
                "id": e["id"],
                "outfit_id": e.get("outfit_id"),
                "scheduled_date": e["scheduled_date"],
                "event_label": e.get("event_label"),
                "status": e["status"],
                "outfit_snapshot": {
                    "schema_version": snap.get("schema_version", 1),
                    "outfit_id": snap.get("outfit_id"),
                    "outfit_name": snap.get("outfit_name"),
                    "items": clean_snap_items,
                },
                "created_at": e["created_at"],
                "updated_at": e["updated_at"],
            }
        )

    clean_wear_logs = [
        {
            "id": wl["id"],
            "planner_entry_id": wl["planner_entry_id"],
            "worn_date": wl["worn_date"],
            "items": [
                {
                    "item_id": wli["item_id"],
                    "item_name_snapshot": wli["item_name_snapshot"],
                }
                for wli in wl.get("items", [])
            ],
            "created_at": wl["created_at"],
        }
        for wl in raw_snapshot.get("wear_logs", [])
    ]

    clean_notifications = [
        {
            "id": n["id"],
            "type": n["type"],
            "title": n["title"],
            "body": n["body"],
            "read_at": n.get("read_at"),
            "created_at": n["created_at"],
        }
        for n in raw_snapshot.get("notifications", [])
    ]

    clean_support = [
        {
            "id": s["id"],
            "reference_code": s["reference_code"],
            "category": s["category"],
            "subject": s["subject"],
            "description": s["description"],
            "status": s["status"],
            "created_at": s["created_at"],
            "closed_at": s.get("closed_at"),
        }
        for s in raw_snapshot.get("support_requests", [])
    ]

    payload = {
        "schema_version": "1.0",
        "snapshot_at": raw_snapshot["snapshot_at"],
        "note": "Bản sao dữ liệu ứng dụng JSON (không bao gồm tập tin ảnh; ảnh có thể tải riêng tại chi tiết từng món đồ).",
        "profile": clean_profile,
        "settings": clean_settings,
        "consents": clean_consents,
        "media_assets": clean_assets,
        "wardrobe_items": clean_items,
        "outfits": clean_outfits,
        "planner_entries": clean_entries,
        "wear_logs": clean_wear_logs,
        "notifications": clean_notifications,
        "support_requests": clean_support,
    }
    return _serialize_value(payload)


def process_pending_data_exports(store: TransactionalStore | None = None) -> int:
    """Claim and process queued data export requests with lease fencing token and REPEATABLE READ snapshot."""
    target_store = store or get_store()
    cfg = get_settings()
    notif_repo = NotificationsRepository(target_store)
    processed = 0

    while True:
        claimed_id: UUID | None = None
        lease_token = uuid4()
        now = utc_now()

        with target_store.lock:
            for req_id, req in target_store.data_export_requests.items():
                is_queued = req["status"] == "queued" and req["available_at"] <= now
                is_stale_running = (
                    req["status"] == "running"
                    and req.get("lease_until") is not None
                    and req["lease_until"] <= now
                )
                if is_queued or is_stale_running:
                    owner_id = req["owner_id"]
                    if target_store.is_account_deleting(owner_id):
                        req["status"] = "cancelled"
                        req["updated_at"] = now
                        continue
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
            req = target_store.data_export_requests[claimed_id]
            owner_id = req["owner_id"]
            attempt_no = req["attempts"]

        # Take atomic snapshot (REPEATABLE READ equivalent)
        try:
            if target_store.is_account_deleting(owner_id):
                with target_store.lock:
                    req = target_store.data_export_requests.get(claimed_id)
                    if req and req.get("lease_token") == lease_token:
                        req["status"] = "cancelled"
                        req["lease_token"] = None
                        req["lease_until"] = None
                continue

            raw_snapshot = target_store.snapshot_for_user(owner_id)
            export_payload = build_whitelisted_export_payload(raw_snapshot)
            json_bytes = json.dumps(
                export_payload, ensure_ascii=False, indent=2
            ).encode("utf-8")

            object_path = (
                f"{owner_id}/{claimed_id}/attempt-{attempt_no}/export.json"
            )
            # Write object first before committing status='ready'
            target_store.put_storage_object(
                cfg.storage_bucket_exports, object_path, json_bytes
            )

            with target_store.lock:
                req = target_store.data_export_requests.get(claimed_id)
                if (
                    req is None
                    or req["status"] != "running"
                    or req.get("lease_token") != lease_token
                    or target_store.is_account_deleting(owner_id)
                ):
                    # Fencing token invalid or account deleting: clean up late/stale output
                    target_store.delete_storage_object(
                        cfg.storage_bucket_exports, object_path
                    )
                    if req and target_store.is_account_deleting(owner_id):
                        req["status"] = "cancelled"
                        req["lease_token"] = None
                        req["lease_until"] = None
                    continue

                finish_now = utc_now()
                req["status"] = "ready"
                req["snapshot_at"] = raw_snapshot["snapshot_at"]
                req["object_path"] = object_path
                req["expires_at"] = finish_now + timedelta(
                    hours=cfg.data_export_ttl_hours
                )
                req["lease_token"] = None
                req["lease_until"] = None
                req["error_code"] = None
                req["updated_at"] = finish_now

                notif_repo.create_notification_if_enabled(
                    owner_id=owner_id,
                    event_key=f"data_export:{claimed_id}:ready",
                    notif_type="data_export_ready",
                    title="Bản sao dữ liệu đã sẵn sàng",
                    body="Bản sao dữ liệu JSON của bạn đã chuẩn bị xong và có hiệu lực tải xuống trong 24 giờ.",
                    target_type="data_export",
                    target_id=claimed_id,
                )
                processed += 1

        except Exception:
            with target_store.lock:
                req = target_store.data_export_requests.get(claimed_id)
                if req and req.get("lease_token") == lease_token:
                    req["lease_token"] = None
                    req["lease_until"] = None
                    req["updated_at"] = utc_now()
                    if req["attempts"] >= MAX_EXPORT_ATTEMPTS:
                        req["status"] = "failed"
                        req["error_code"] = "EXPORT_GENERATION_FAILED"
                        notif_repo.create_notification_if_enabled(
                            owner_id=owner_id,
                            event_key=f"data_export:{claimed_id}:failed",
                            notif_type="data_export_failed",
                            title="Không thể tạo bản sao dữ liệu",
                            body="Đã xảy ra lỗi khi chuẩn bị bản sao dữ liệu. Bạn có thể gửi lại yêu cầu trong Cài đặt.",
                            target_type="settings_privacy",
                            target_id=claimed_id,
                        )
                    else:
                        req["status"] = "queued"
                        req["available_at"] = utc_now() + timedelta(
                            seconds=30 * req["attempts"]
                        )

    return processed


if __name__ == "__main__":
    count = process_pending_data_exports()
    print(f"Processed {count} data export request(s).")

