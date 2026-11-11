import json

import pytest
from httpx import AsyncClient

from app.infrastructure.supabase.client import TransactionalStore
from scripts.process_account_deletions import process_pending_account_deletions
from scripts.process_data_exports import process_pending_data_exports


@pytest.mark.asyncio
async def test_unverified_user_cannot_bootstrap(
    client: AsyncClient, headers_unverified: dict[str, str]
) -> None:
    resp = await client.post(
        "/api/v1/accounts/bootstrap",
        headers=headers_unverified,
        json={
            "terms_version": "2026-11",
            "privacy_version": "2026-11",
            "accept_terms": True,
            "acknowledge_privacy": True,
        },
    )
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "EMAIL_NOT_VERIFIED"


@pytest.mark.asyncio
async def test_bootstrap_profile_settings_and_consents(
    client: AsyncClient, headers_a: dict[str, str]
) -> None:
    # Before bootstrap, /accounts/me returns 404 PROFILE_NOT_READY
    pre = await client.get("/api/v1/accounts/me", headers=headers_a)
    assert pre.status_code == 404
    assert pre.json()["error"]["code"] == "PROFILE_NOT_READY"

    # Outdated policy version rejected with 400 POLICY_ACCEPTANCE_REQUIRED
    bad = await client.post(
        "/api/v1/accounts/bootstrap",
        headers=headers_a,
        json={
            "terms_version": "2025-01",
            "privacy_version": "2026-11",
            "accept_terms": True,
            "acknowledge_privacy": True,
        },
    )
    assert bad.status_code == 400
    assert bad.json()["error"]["code"] == "POLICY_ACCEPTANCE_REQUIRED"

    # First valid bootstrap returns 201
    res1 = await client.post(
        "/api/v1/accounts/bootstrap",
        headers=headers_a,
        json={
            "terms_version": "2026-11",
            "privacy_version": "2026-11",
            "accept_terms": True,
            "acknowledge_privacy": True,
            "display_name": "Alice",
        },
    )
    assert res1.status_code == 201
    prof = res1.json()["data"]
    assert prof["display_name"] == "Alice"
    assert prof["timezone"] == "Asia/Ho_Chi_Minh"
    assert prof["version"] == 1
    assert prof["account_status"] == "active"

    # Second bootstrap retry returns 200 and does NOT overwrite display_name
    res2 = await client.post(
        "/api/v1/accounts/bootstrap",
        headers=headers_a,
        json={
            "terms_version": "2026-11",
            "privacy_version": "2026-11",
            "accept_terms": True,
            "acknowledge_privacy": True,
            "display_name": "Other Name",
        },
    )
    assert res2.status_code == 200
    assert res2.json()["data"]["display_name"] == "Alice"

    # Update profile with version conflict check
    upd = await client.patch(
        "/api/v1/accounts/me",
        headers=headers_a,
        json={"display_name": "Alice Nguyễn", "expected_version": 1},
    )
    assert upd.status_code == 200
    assert upd.json()["data"]["version"] == 2

    conflict = await client.patch(
        "/api/v1/accounts/me",
        headers=headers_a,
        json={"display_name": "Stale Tab", "expected_version": 1},
    )
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "CONFLICT"

    # Onboarding skip is idempotent
    onb = await client.post(
        "/api/v1/accounts/me/onboarding",
        headers=headers_a,
        json={"action": "skip"},
    )
    assert onb.status_code == 200
    skipped_at = onb.json()["data"]["onboarding_skipped_at"]
    assert skipped_at is not None

    onb_repeat = await client.post(
        "/api/v1/accounts/me/onboarding",
        headers=headers_a,
        json={"action": "skip"},
    )
    assert onb_repeat.json()["data"]["onboarding_skipped_at"] == skipped_at

    # Settings update records analytics consent in same transaction
    s_get = await client.get("/api/v1/settings", headers=headers_a)
    assert s_get.status_code == 200
    assert s_get.json()["data"]["analytics_opt_in"] is False

    s_patch = await client.patch(
        "/api/v1/settings",
        headers=headers_a,
        json={
            "planner_default_view": "month",
            "analytics_opt_in": True,
            "expected_version": 1,
        },
    )
    assert s_patch.status_code == 200
    assert s_patch.json()["data"]["version"] == 2
    assert s_patch.json()["data"]["analytics_opt_in"] is True

    # AI consent revision and idempotency
    ai_consent = await client.post(
        "/api/v1/accounts/me/consents",
        headers=headers_a,
        json={
            "kind": "ai",
            "policy_version": "2026-11-photoroom",
            "action": "accepted",
            "request_key": "ai-consent-1",
            "expected_revision": 0,
        },
    )
    assert ai_consent.status_code == 200
    assert ai_consent.json()["data"]["revision"] == 1

    # Stale revision with a new request_key is rejected with 409
    stale_ai = await client.post(
        "/api/v1/accounts/me/consents",
        headers=headers_a,
        json={
            "kind": "ai",
            "policy_version": "2026-11-photoroom",
            "action": "withdrawn",
            "request_key": "ai-consent-2",
            "expected_revision": 0,
        },
    )
    assert stale_ai.status_code == 409


@pytest.mark.asyncio
async def test_support_data_export_notifications_and_account_deletion(
    client: AsyncClient,
    test_store: TransactionalStore,
    headers_a: dict[str, str],
    headers_b: dict[str, str],
) -> None:
    # Bootstrap both users
    for hdrs in (headers_a, headers_b):
        await client.post(
            "/api/v1/accounts/bootstrap",
            headers=hdrs,
            json={
                "terms_version": "2026-11",
                "privacy_version": "2026-11",
                "accept_terms": True,
                "acknowledge_privacy": True,
            },
        )

    # Support request: extra unknown diagnostics field rejected with 422
    bad_diag = await client.post(
        "/api/v1/support/requests",
        headers=headers_a,
        json={
            "request_key": "sup-bad",
            "category": "bug",
            "subject": "Lỗi tải ảnh lên tủ đồ",
            "description": "Khi tôi chọn ảnh PNG 2MB thì màn hình báo lỗi.",
            "diagnostics": {
                "app_version": "0.1.0",
                "cookie": "secret-session-cookie",
            },
        },
    )
    assert bad_diag.status_code == 422

    # Valid support request
    sup1 = await client.post(
        "/api/v1/support/requests",
        headers=headers_a,
        json={
            "request_key": "sup-1",
            "category": "bug",
            "subject": "Lỗi tải ảnh lên tủ đồ",
            "description": "Khi tôi chọn ảnh PNG 2MB thì màn hình báo lỗi.",
            "diagnostics": {"app_version": "0.1.0", "browser_family": "Chrome"},
        },
    )
    assert sup1.status_code == 201
    sup_id = sup1.json()["data"]["id"]

    # Replay same request_key + same content -> 200
    sup_replay = await client.post(
        "/api/v1/support/requests",
        headers=headers_a,
        json={
            "request_key": "sup-1",
            "category": "bug",
            "subject": "Lỗi tải ảnh lên tủ đồ",
            "description": "Khi tôi chọn ảnh PNG 2MB thì màn hình báo lỗi.",
            "diagnostics": {"app_version": "0.1.0", "browser_family": "Chrome"},
        },
    )
    assert sup_replay.status_code == 200
    assert sup_replay.json()["data"]["id"] == sup_id

    # Replay same request_key + different content -> 409
    sup_conflict = await client.post(
        "/api/v1/support/requests",
        headers=headers_a,
        json={
            "request_key": "sup-1",
            "category": "feedback",
            "subject": "Nội dung khác hoàn toàn",
            "description": "Nội dung mô tả khác với phiếu ban đầu đã gửi.",
        },
    )
    assert sup_conflict.status_code == 409

    # User B cannot read User A's support ticket -> 404
    sup_b = await client.get(f"/api/v1/support/requests/{sup_id}", headers=headers_b)
    assert sup_b.status_code == 404

    # Data export request + background worker + notification + private download
    exp_create = await client.post(
        "/api/v1/data-exports",
        headers=headers_a,
        json={"request_key": "exp-1"},
    )
    assert exp_create.status_code == 202
    export_id = exp_create.json()["data"]["id"]

    # Run worker to generate snapshot and notification
    processed = process_pending_data_exports(test_store)
    assert processed == 1

    # Check notification created
    unread = await client.get("/api/v1/notifications/unread-count", headers=headers_a)
    assert unread.json()["data"]["unread_count"] == 1

    notifs = await client.get("/api/v1/notifications", headers=headers_a)
    assert len(notifs.json()["data"]) == 1
    assert notifs.json()["data"][0]["type"] == "data_export_ready"

    # Mark all notifications read
    read_all = await client.post("/api/v1/notifications/read-all", headers=headers_a)
    assert read_all.json()["data"]["updated_count"] == 1

    # Download export JSON (User B gets 404, User A gets attachment stream)
    dl_b = await client.get(
        f"/api/v1/data-exports/{export_id}/download", headers=headers_b
    )
    assert dl_b.status_code == 404

    dl_a = await client.get(
        f"/api/v1/data-exports/{export_id}/download", headers=headers_a
    )
    assert dl_a.status_code == 200
    assert dl_a.headers["cache-control"] == "private, no-store"
    assert "attachment;" in dl_a.headers["content-disposition"]
    exported_json = json.loads(dl_a.content.decode("utf-8"))
    assert exported_json["schema_version"] == "1.0"
    assert exported_json["profile"]["display_name"] == "Bạn"
    assert len(exported_json["support_requests"]) == 1

    # Account deletion: wrong password rejected with 401
    del_bad = await client.request(
        "DELETE",
        "/api/v1/accounts/me",
        headers=headers_a,
        json={
            "current_password": "WrongPassword",
            "confirmation": "XÓA TÀI KHOẢN",
            "request_key": "del-1",
        },
    )
    assert del_bad.status_code == 401

    # Valid account deletion request returns 202 Accepted
    del_ok = await client.request(
        "DELETE",
        "/api/v1/accounts/me",
        headers=headers_a,
        json={
            "current_password": "AliceSecretPassword123!",
            "confirmation": "XÓA TÀI KHOẢN",
            "request_key": "del-1",
        },
    )
    assert del_ok.status_code == 202
    assert del_ok.json()["data"]["status"] == "requested"

    # Mutations while account is deleting are blocked with 403 ACCOUNT_DELETION_PENDING
    mut_blocked = await client.patch(
        "/api/v1/accounts/me",
        headers=headers_a,
        json={"display_name": "Blocked", "expected_version": 1},
    )
    assert mut_blocked.status_code == 403
    assert mut_blocked.json()["error"]["code"] == "ACCOUNT_DELETION_PENDING"

    # Worker processes account deletion and wipes storage & tables
    deleted_count = process_pending_account_deletions(
        test_store, ignore_upload_expiry_for_test=True
    )
    assert deleted_count == 1
    assert len(test_store.storage_objects["account-exports"]) == 0

