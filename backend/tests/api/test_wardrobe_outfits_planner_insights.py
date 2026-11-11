import base64
from datetime import date, timedelta

import pytest
from httpx import AsyncClient

from app.infrastructure.supabase.client import TransactionalStore
from app.modules.image_jobs.router import get_image_jobs_service
from app.modules.image_jobs.service import ImageJobsService
from tests.conftest import make_test_image_bytes


class FakeBackgroundRemovalProvider:
    async def remove_background(
        self, image_bytes: bytes, content_type: str = "image/png"
    ) -> bytes:
        return make_test_image_bytes(width=120, height=160, fmt="PNG", rgba=True)


@pytest.mark.asyncio
async def test_full_wardrobe_outfits_planner_and_girl_math_lifecycle(
    client: AsyncClient,
    test_store: TransactionalStore,
    headers_a: dict[str, str],
    headers_b: dict[str, str],
) -> None:
    # Override AI provider with deterministic fake cutout generator
    from app.main import app

    app.dependency_overrides[get_image_jobs_service] = lambda: ImageJobsService(
        test_store, ai_provider=FakeBackgroundRemovalProvider()
    )

    # 1. Bootstrap User A and User B
    for hdrs in (headers_a, headers_b):
        res = await client.post(
            "/api/v1/accounts/bootstrap",
            headers=hdrs,
            json={
                "terms_version": "2026-11",
                "privacy_version": "2026-11",
                "accept_terms": True,
                "acknowledge_privacy": True,
            },
        )
        assert res.status_code == 201

    # 2. Upload and finalize an image via Rust image_core
    up_res = await client.post(
        "/api/v1/media/uploads",
        headers=headers_a,
        json={
            "filename": "cardigan.jpg",
            "content_type": "image/jpeg",
            "byte_size": 2048,
        },
    )
    assert up_res.status_code == 201
    asset_id = up_res.json()["data"]["asset_id"]

    raw_jpg_b64 = base64.b64encode(
        make_test_image_bytes(width=300, height=400, fmt="JPEG")
    ).decode("ascii")
    fin_res = await client.post(
        f"/api/v1/media/uploads/{asset_id}/finalize",
        headers=headers_a,
        json={"staged_bytes_b64": raw_jpg_b64},
    )
    assert fin_res.status_code == 200
    assert fin_res.json()["data"]["status"] == "ready"
    assert "original" in fin_res.json()["data"]["available_variants"]

    # 3. AI background removal requires AI consent first
    no_consent_job = await client.post(
        "/api/v1/image-jobs",
        headers=headers_a,
        json={"asset_id": asset_id, "request_key": "job-1"},
    )
    assert no_consent_job.status_code == 403
    assert no_consent_job.json()["error"]["code"] == "AI_CONSENT_REQUIRED"

    await client.post(
        "/api/v1/accounts/me/consents",
        headers=headers_a,
        json={
            "kind": "ai",
            "policy_version": "2026-11-photoroom",
            "action": "accepted",
            "request_key": "consent-ai-1",
            "expected_revision": 0,
        },
    )

    job_res = await client.post(
        "/api/v1/image-jobs",
        headers=headers_a,
        json={"asset_id": asset_id, "request_key": "job-1"},
    )
    assert job_res.status_code == 201
    assert job_res.json()["data"]["status"] == "succeeded"

    # Download cutout media
    dl_cutout = await client.get(
        f"/api/v1/media/{asset_id}/download?variant=cutout", headers=headers_a
    )
    assert dl_cutout.status_code == 200
    assert dl_cutout.headers["content-type"] == "image/png"

    # 4. Create 3 wardrobe items:
    # - Item 1: Cardigan kem (photo with cutout, price 300,000 VND)
    # - Item 2: Quần jeans (placeholder, price 0 VND)
    # - Item 3: Túi xách (placeholder, price None / missing_price)
    item1_res = await client.post(
        "/api/v1/wardrobe/items",
        headers=headers_a,
        json={
            "name": "Cardigan kem",
            "category": "top",
            "source": "photo",
            "asset_id": asset_id,
            "image_variant": "cutout",
            "colors": ["cream"],
            "purchase_price_vnd": 300_000,
        },
    )
    assert item1_res.status_code == 201
    item1_id = item1_res.json()["data"]["id"]

    item2_res = await client.post(
        "/api/v1/wardrobe/items",
        headers=headers_a,
        json={
            "name": "Quần jeans xanh",
            "category": "bottom",
            "source": "placeholder",
            "colors": ["blue"],
            "purchase_price_vnd": 0,
        },
    )
    assert item2_res.status_code == 201
    item2_id = item2_res.json()["data"]["id"]

    item3_res = await client.post(
        "/api/v1/wardrobe/items",
        headers=headers_a,
        json={
            "name": "Túi đeo vai",
            "category": "bag",
            "source": "placeholder",
            "colors": ["black"],
        },
    )
    assert item3_res.status_code == 201
    item3_id = item3_res.json()["data"]["id"]
    assert item3_res.json()["data"]["purchase_price_vnd"] is None
    assert item3_res.json()["data"]["cpw_status"] == "missing_price"

    # User B cannot access User A's item -> 404
    b_get = await client.get(f"/api/v1/wardrobe/items/{item1_id}", headers=headers_b)
    assert b_get.status_code == 404

    # 5. Create 2 outfits sharing Item 1 (Cardigan kem)
    outfit1_res = await client.post(
        "/api/v1/outfits",
        headers=headers_a,
        json={
            "name": "Đi làm sáng",
            "items": [
                {"item_id": item1_id, "x": 0.1, "y": 0.1, "w": 0.4, "h": 0.4, "z_index": 0},
                {"item_id": item2_id, "x": 0.1, "y": 0.5, "w": 0.4, "h": 0.4, "z_index": 1},
            ],
        },
    )
    assert outfit1_res.status_code == 201
    outfit1_id = outfit1_res.json()["data"]["id"]

    outfit2_res = await client.post(
        "/api/v1/outfits",
        headers=headers_a,
        json={
            "name": "Đi cà phê tối",
            "items": [
                {"item_id": item1_id, "x": 0.2, "y": 0.1, "w": 0.5, "h": 0.4, "z_index": 0},
                {"item_id": item3_id, "x": 0.3, "y": 0.6, "w": 0.3, "h": 0.3, "z_index": 1},
            ],
        },
    )
    assert outfit2_res.status_code == 201
    outfit2_id = outfit2_res.json()["data"]["id"]

    # 6. Schedule both outfits on the same day (today)
    today_str = date.today().isoformat()
    entry1_res = await client.post(
        "/api/v1/planner/entries",
        headers=headers_a,
        json={
            "outfit_id": outfit1_id,
            "scheduled_date": today_str,
            "event_label": "Đi làm",
        },
    )
    assert entry1_res.status_code == 201
    entry1_id = entry1_res.json()["data"]["id"]

    entry2_res = await client.post(
        "/api/v1/planner/entries",
        headers=headers_a,
        json={
            "outfit_id": outfit2_id,
            "scheduled_date": today_str,
            "event_label": "Cà phê",
        },
    )
    assert entry2_res.status_code == 201
    entry2_id = entry2_res.json()["data"]["id"]

    # Future date entry cannot be confirmed as worn
    tomorrow_str = (date.today() + timedelta(days=2)).isoformat()
    future_entry_res = await client.post(
        "/api/v1/planner/entries",
        headers=headers_a,
        json={"outfit_id": outfit1_id, "scheduled_date": tomorrow_str},
    )
    future_entry_id = future_entry_res.json()["data"]["id"]
    future_confirm = await client.post(
        f"/api/v1/planner/entries/{future_entry_id}/confirm-wear",
        headers=headers_a,
        json={"operation_key": "op-future", "expected_version": 1},
    )
    assert future_confirm.status_code == 400

    # 7. Confirm wear on both entries for today
    c1 = await client.post(
        f"/api/v1/planner/entries/{entry1_id}/confirm-wear",
        headers=headers_a,
        json={"operation_key": "op-confirm-1", "expected_version": 1},
    )
    assert c1.status_code == 200
    assert c1.json()["data"]["status"] == "worn"
    assert c1.json()["data"]["version"] == 2

    # Idempotent replay with same operation_key
    c1_replay = await client.post(
        f"/api/v1/planner/entries/{entry1_id}/confirm-wear",
        headers=headers_a,
        json={"operation_key": "op-confirm-1", "expected_version": 1},
    )
    assert c1_replay.status_code == 200
    assert c1_replay.json()["data"]["version"] == 2

    c2 = await client.post(
        f"/api/v1/planner/entries/{entry2_id}/confirm-wear",
        headers=headers_a,
        json={"operation_key": "op-confirm-2", "expected_version": 1},
    )
    assert c2.status_code == 200
    assert c2.json()["data"]["status"] == "worn"

    # 8. Check Girl Math insights:
    # Item 1 was worn in 2 outfits on the SAME day -> wear_days_count MUST be 1!
    # Total distinct (item, date) pairs across closet = (item1, today), (item2, today), (item3, today) = 3!
    summary_res = await client.get("/api/v1/insights/summary", headers=headers_a)
    assert summary_res.status_code == 200
    assert summary_res.json()["data"] == {
        "active_items_count": 3,
        "active_outfits_count": 2,
        "total_wear_count": 3,
    }

    cpw_res = await client.get("/api/v1/insights/cost-per-wear", headers=headers_a)
    assert cpw_res.status_code == 200
    cpw_by_id = {row["item_id"]: row for row in cpw_res.json()["data"]}
    assert cpw_by_id[item1_id]["wear_days_count"] == 1
    assert cpw_by_id[item1_id]["display_cost_per_wear_vnd"] == 300_000
    assert cpw_by_id[item2_id]["wear_days_count"] == 1
    assert cpw_by_id[item2_id]["display_cost_per_wear_vnd"] == 0
    assert cpw_by_id[item3_id]["wear_days_count"] == 1
    assert cpw_by_id[item3_id]["cpw_status"] == "missing_price"

    # 9. Unconfirm entry 2:
    # Item 1 is STILL worn in entry 1 today -> wear_days_count for Item 1 stays 1!
    # Item 3 was only in entry 2 -> wear_days_count for Item 3 becomes 0!
    unc2 = await client.post(
        f"/api/v1/planner/entries/{entry2_id}/unconfirm-wear",
        headers=headers_a,
        json={"operation_key": "op-unconfirm-2", "expected_version": 2},
    )
    assert unc2.status_code == 200
    assert unc2.json()["data"]["status"] == "planned"
    assert unc2.json()["data"]["version"] == 3

    # Stale retry of an old confirm with expected_version=1 is rejected with 409 CONFLICT
    stale_confirm = await client.post(
        f"/api/v1/planner/entries/{entry2_id}/confirm-wear",
        headers=headers_a,
        json={"operation_key": "op-old-retry", "expected_version": 1},
    )
    assert stale_confirm.status_code == 409

    summary_after = await client.get("/api/v1/insights/summary", headers=headers_a)
    assert summary_after.json()["data"]["total_wear_count"] == 2

    item1_detail = await client.get(
        f"/api/v1/wardrobe/items/{item1_id}", headers=headers_a
    )
    assert item1_detail.json()["data"]["wear_days_count"] == 1

