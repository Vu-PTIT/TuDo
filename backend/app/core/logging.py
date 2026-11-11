import logging
import re
from typing import Any

SENSITIVE_KEYS = frozenset(
    {
        "password",
        "current_password",
        "new_password",
        "token",
        "access_token",
        "refresh_token",
        "authorization",
        "secret",
        "api_key",
        "signed_url",
        "upload_url",
        "image_bytes",
    }
)

BEARER_PATTERN = re.compile(r"Bearer\s+[A-Za-z0-9\-._~+/]+=*", re.IGNORECASE)


def sanitize_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Recursively redact sensitive fields so passwords/tokens/bytes never leak into logs."""
    cleaned: dict[str, Any] = {}
    for k, v in data.items():
        if isinstance(v, (bytes, bytearray)):
            cleaned[k] = f"<bytes len={len(v)}>"
        elif k.lower() in SENSITIVE_KEYS:
            cleaned[k] = "[REDACTED]"
        elif isinstance(v, dict):
            cleaned[k] = sanitize_dict(v)
        elif isinstance(v, str):
            cleaned[k] = BEARER_PATTERN.sub("Bearer [REDACTED]", v)
        else:
            cleaned[k] = v
    return cleaned


class RedactingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = BEARER_PATTERN.sub("Bearer [REDACTED]", record.msg)
        return True


def configure_logging() -> logging.Logger:
    logger = logging.getLogger("closet_loop")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.addFilter(RedactingFilter())
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s [%(name)s] %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


logger = configure_logging()
