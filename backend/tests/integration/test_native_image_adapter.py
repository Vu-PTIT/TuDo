import pytest

from app.core.errors import AppError
from app.infrastructure.native.image_core import (
    is_native_available,
    normalize_image_async,
    validate_cutout_async,
)
from tests.conftest import make_test_image_bytes


@pytest.mark.asyncio
async def test_native_module_is_loaded() -> None:
    assert is_native_available() is True


@pytest.mark.asyncio
async def test_normalize_image_and_thumbnail() -> None:
    raw_jpeg = make_test_image_bytes(width=800, height=600, fmt="JPEG")
    result = await normalize_image_async(
        raw_jpeg,
        max_dimension=400,
        thumbnail_size=100,
    )
    assert result.width == 400
    assert result.height == 300
    assert result.thumbnail_width == 100
    assert result.thumbnail_height == 75
    assert result.format == "jpeg"
    assert result.has_alpha is False
    assert len(result.image_bytes) > 0
    assert len(result.thumbnail_bytes) > 0


@pytest.mark.asyncio
async def test_rejects_heic_and_gif_with_unsupported_format() -> None:
    heic_bytes = b"\x00\x00\x00\x18ftypheic\x00\x00\x00\x00"
    with pytest.raises(AppError) as exc_info:
        await normalize_image_async(heic_bytes)
    assert exc_info.value.code == "UNSUPPORTED_FORMAT"

    gif_bytes = make_test_image_bytes(width=32, height=32, fmt="GIF")
    with pytest.raises(AppError) as exc_info2:
        await normalize_image_async(gif_bytes)
    assert exc_info2.value.code == "UNSUPPORTED_FORMAT"


@pytest.mark.asyncio
async def test_rejects_oversized_bytes_and_pixels() -> None:
    raw_png = make_test_image_bytes(width=100, height=100, fmt="PNG")
    with pytest.raises(AppError) as exc_info:
        await normalize_image_async(raw_png, max_bytes=10)
    assert exc_info.value.code == "IMAGE_TOO_LARGE"

    with pytest.raises(AppError) as exc_info2:
        await normalize_image_async(raw_png, max_pixels=500)
    assert exc_info2.value.code == "IMAGE_TOO_LARGE"


@pytest.mark.asyncio
async def test_validate_cutout_requires_alpha() -> None:
    opaque_jpeg = make_test_image_bytes(width=64, height=64, fmt="JPEG", rgba=False)
    with pytest.raises(AppError) as exc_info:
        await validate_cutout_async(opaque_jpeg)
    assert exc_info.value.code == "INVALID_IMAGE"

    rgba_png = make_test_image_bytes(width=64, height=64, fmt="PNG", rgba=True)
    cutout_res = await validate_cutout_async(rgba_png)
    assert cutout_res.has_alpha is True
    assert cutout_res.format == "png"

