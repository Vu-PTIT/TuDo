from typing import Protocol

import httpx
from fastapi import status

from app.core.config import get_settings
from app.core.errors import AppError


class BackgroundRemovalProvider(Protocol):
    async def remove_background(self, image_bytes: bytes, content_type: str = "image/png") -> bytes: ...


class PhotoroomBackgroundRemovalClient:
    """Calls external background removal API with strict timeout and never leaks API keys."""

    ENDPOINT = "https://sdk.photoroom.com/v1/segment"

    def __init__(self, api_key: str | None = None, timeout_seconds: float | None = None) -> None:
        cfg = get_settings()
        self._api_key = api_key if api_key is not None else cfg.ai_api_key
        self._timeout = timeout_seconds if timeout_seconds is not None else cfg.ai_timeout_seconds

    async def remove_background(self, image_bytes: bytes, content_type: str = "image/png") -> bytes:
        if not self._api_key:
            raise AppError(
                code="IMAGE_PROCESSING_FAILED",
                message="Dịch vụ tách nền AI chưa được cấu hình. Bạn vẫn có thể lưu ảnh ban đầu.",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(self._timeout)) as client:
                response = await client.post(
                    self.ENDPOINT,
                    headers={"x-api-key": self._api_key},
                    files={"image_file": ("item.png", image_bytes, content_type)},
                )
        except httpx.TimeoutException as exc:
            raise AppError(
                code="IMAGE_PROCESSING_TIMEOUT",
                message="Quá thời gian xử lý tách nền. Bạn có thể giữ ảnh ban đầu hoặc thử lại.",
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            ) from exc
        except httpx.HTTPError as exc:
            raise AppError(
                code="IMAGE_PROCESSING_FAILED",
                message="Không thể kết nối dịch vụ tách nền. Bạn có thể giữ ảnh ban đầu.",
                status_code=status.HTTP_502_BAD_GATEWAY,
            ) from exc

        if response.status_code != status.HTTP_200_OK:
            raise AppError(
                code="IMAGE_PROCESSING_FAILED",
                message="Dịch vụ tách nền không thể xử lý ảnh này. Bạn có thể giữ ảnh ban đầu.",
                status_code=status.HTTP_502_BAD_GATEWAY,
            )

        return response.content

