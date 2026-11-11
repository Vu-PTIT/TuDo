from uuid import UUID

from app.core.config import get_settings
from app.infrastructure.supabase.client import TransactionalStore, get_store, utc_now


def cleanup_abandoned_and_unreferenced_media(
    store: TransactionalStore | None = None,
) -> dict[str, int]:
    """Clean up expired staging uploads and unreferenced media assets while preserving planner history snapshots."""
    target_store = store or get_store()
    cfg = get_settings()
    now = utc_now()
    expired_staging_cleaned = 0
    orphan_assets_cleaned = 0

    with target_store.lock:
        # 1. Collect all asset_ids referenced by wardrobe_items (including soft-deleted) or planner snapshots
        referenced_assets: set[UUID] = set()
        for item in target_store.wardrobe_items.values():
            if item.get("asset_id"):
                referenced_assets.add(item["asset_id"])

        for entry in target_store.planner_entries.values():
            snap = entry.get("outfit_snapshot", {})
            for s_item in snap.get("items", []):
                if s_item.get("asset_id"):
                    referenced_assets.add(UUID(str(s_item["asset_id"])))

        # 2. Clean expired upload_pending assets
        for asset_id, asset in list(target_store.media_assets.items()):
            if (
                asset["status"] == "upload_pending"
                and asset.get("upload_expires_at") is not None
                and asset["upload_expires_at"] <= now
            ):
                if asset.get("staging_path"):
                    target_store.delete_storage_object(
                        cfg.storage_bucket_wardrobe, asset["staging_path"]
                    )
                asset["status"] = "rejected"
                asset["staging_path"] = None
                asset["updated_at"] = now
                expired_staging_cleaned += 1

            elif (
                asset["status"] == "ready"
                and asset_id not in referenced_assets
                and (now - asset["created_at"]).total_seconds() > 3600
            ):
                # Asset ready > 1 hour ago but never attached to any item or planner snapshot
                for p_key in ("original_path", "cutout_path"):
                    if asset.get(p_key):
                        target_store.delete_storage_object(
                            cfg.storage_bucket_wardrobe, asset[p_key]
                        )
                for v_meta in asset.get("variant_metadata", {}).values():
                    if v_meta.get("thumbnail_path"):
                        target_store.delete_storage_object(
                            cfg.storage_bucket_wardrobe, v_meta["thumbnail_path"]
                        )
                target_store.media_assets.pop(asset_id, None)
                orphan_assets_cleaned += 1

    return {
        "expired_staging_cleaned": expired_staging_cleaned,
        "orphan_assets_cleaned": orphan_assets_cleaned,
    }


if __name__ == "__main__":
    stats = cleanup_abandoned_and_unreferenced_media()
    print(f"Media cleanup complete: {stats}")

