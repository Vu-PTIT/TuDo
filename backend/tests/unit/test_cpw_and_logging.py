from app.core.logging import sanitize_dict
from app.modules.wardrobe.service import compute_cpw_metrics


def test_cpw_missing_price() -> None:
    raw, display, status = compute_cpw_metrics(None, 5)
    assert raw is None
    assert display is None
    assert status == "missing_price"


def test_cpw_unworn() -> None:
    raw, display, status = compute_cpw_metrics(300_000, 0)
    assert raw is None
    assert display is None
    assert status == "unworn"


def test_cpw_zero_price_worn() -> None:
    raw, display, status = compute_cpw_metrics(0, 3)
    assert raw == 0.0
    assert display == 0
    assert status == "calculated"


def test_cpw_standard_and_rounding() -> None:
    # 300,000 VND / 10 days = 30,000 VND
    raw, display, status = compute_cpw_metrics(300_000, 10)
    assert raw == 30_000.0
    assert display == 30_000
    assert status == "calculated"

    # 100,000 VND / 3 days = 33,333.333... -> rounded display 33,333
    raw2, display2, status2 = compute_cpw_metrics(100_000, 3)
    assert raw2 is not None and abs(raw2 - 33333.3333) < 0.01
    assert display2 == 33_333
    assert status2 == "calculated"


def test_sanitize_dict_redacts_secrets_and_bytes() -> None:
    payload = {
        "current_password": "MySuperSecretPassword",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.secret",
        "nested": {
            "signed_url": "https://storage.local/secret",
            "image_bytes": b"\x89PNG\r\n",
            "note": "Header Bearer abc.def.ghi in text",
        },
        "safe_field": "cardigan",
    }
    cleaned = sanitize_dict(payload)
    assert cleaned["current_password"] == "[REDACTED]"
    assert cleaned["Authorization"] == "[REDACTED]"
    assert cleaned["nested"]["signed_url"] == "[REDACTED]"
    assert cleaned["nested"]["image_bytes"] == "<bytes len=6>"
    assert "Bearer [REDACTED]" in cleaned["nested"]["note"]
    assert cleaned["safe_field"] == "cardigan"

