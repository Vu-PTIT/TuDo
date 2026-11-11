import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from fastapi import status

from app.core.config import get_settings
from app.core.errors import AppError

try:
    import closet_loop_image_core as _native_core

    NATIVE_EXTENSION_LOADED = True
except ImportError:
    _native_core = None
    NATIVE_EXTENSION_LOADED = False


@dataclass(frozen=True)
class NormalizedImageResult:
    image_bytes: bytes
    thumbnail_bytes: bytes
    width: int
    height: int
    thumbnail_width: int
    thumbnail_height: int
    format: str
    has_alpha: bool


_settings = get_settings()
_executor = ThreadPoolExecutor(
    max_workers=_settings.image_concurrency_limit,
    thread_name_prefix="image_core_worker",
)
_semaphore = asyncio.Semaphore(_settings.image_concurrency_limit)


def is_native_available() -> bool:
    return NATIVE_EXTENSION_LOADED


def _map_native_error(exc: ValueError) -> AppError:
    args = exc.args
    if len(args) == 1 and isinstance(args[0], tuple) and len(args[0]) == 2:
        code, msg = args[0]
    elif len(args) >= 2:
        code, msg = str(args[0]), str(args[1])
    else:
        raw = str(exc)
        if ":" in raw:
            code, msg = raw.split(":", 1)
            code = code.strip()
            msg = msg.strip()
        else:
            code, msg = "INVALID_IMAGE", raw

    if code == "IMAGE_TOO_LARGE":
        return AppError(
            code="IMAGE_TOO_LARGE",
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    if code == "UNSUPPORTED_FORMAT":
        return AppError(
            code="UNSUPPORTED_FORMAT",
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return AppError(
        code="INVALID_IMAGE",
        message=msg,
        status_code=status.HTTP_400_BAD_REQUEST,
    )


def _normalize_sync(
    data: bytes,
    max_bytes: int,
    max_pixels: int,
    max_dimension: int,
    thumbnail_size: int,
) -> NormalizedImageResult:
    if _native_core is None:
        raise AppError(
            code="SERVICE_UNAVAILABLE",
            message="Native Rust image_core module is not loaded.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    try:
        res = _native_core.normalize_image(
            data,
            max_bytes=max_bytes,
            max_pixels=max_pixels,
            max_dimension=max_dimension,
            thumbnail_size=thumbnail_size,
        )
        return NormalizedImageResult(
            image_bytes=bytes(res["image_bytes"]),
            thumbnail_bytes=bytes(res["thumbnail_bytes"]),
            width=int(res["width"]),
            height=int(res["height"]),
            thumbnail_width=int(res["thumbnail_width"]),
            thumbnail_height=int(res["thumbnail_height"]),
            format=str(res["format"]),
            has_alpha=bool(res["has_alpha"]),
        )
    except ValueError as exc:
        raise _map_native_error(exc) from exc


def _validate_cutout_sync(
    data: bytes,
    max_bytes: int,
    max_pixels: int,
    max_dimension: int,
    thumbnail_size: int,
) -> NormalizedImageResult:
    if _native_core is None:
        raise AppError(
            code="SERVICE_UNAVAILABLE",
            message="Native Rust image_core module is not loaded.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    try:
        res = _native_core.validate_cutout(
            data,
            max_bytes=max_bytes,
            max_pixels=max_pixels,
            max_dimension=max_dimension,
            thumbnail_size=thumbnail_size,
        )
        return NormalizedImageResult(
            image_bytes=bytes(res["image_bytes"]),
            thumbnail_bytes=bytes(res["thumbnail_bytes"]),
            width=int(res["width"]),
            height=int(res["height"]),
            thumbnail_width=int(res["thumbnail_width"]),
            thumbnail_height=int(res["thumbnail_height"]),
            format=str(res["format"]),
            has_alpha=bool(res["has_alpha"]),
        )
    except ValueError as exc:
        raise _map_native_error(exc) from exc


async def normalize_image_async(
    data: bytes,
    max_bytes: int | None = None,
    max_pixels: int | None = None,
    max_dimension: int | None = None,
    thumbnail_size: int | None = None,
) -> NormalizedImageResult:
    cfg = get_settings()
    async with _semaphore:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            _executor,
            _normalize_sync,
            data,
            max_bytes if max_bytes is not None else cfg.image_max_bytes,
            max_pixels if max_pixels is not None else cfg.image_max_pixels,
            max_dimension if max_dimension is not None else cfg.image_max_dimension,
            thumbnail_size if thumbnail_size is not None else cfg.image_thumbnail_size,
        )


async def validate_cutout_async(
    data: bytes,
    max_bytes: int | None = None,
    max_pixels: int | None = None,
    max_dimension: int | None = None,
    thumbnail_size: int | None = None,
) -> NormalizedImageResult:
    cfg = get_settings()
    async with _semaphore:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            _executor,
            _validate_cutout_sync,
            data,
            max_bytes if max_bytes is not None else cfg.image_max_bytes,
            max_pixels if max_pixels is not None else cfg.image_max_pixels,
            max_dimension if max_dimension is not None else cfg.image_max_dimension,
            thumbnail_size if thumbnail_size is not None else cfg.image_thumbnail_size,
        )

