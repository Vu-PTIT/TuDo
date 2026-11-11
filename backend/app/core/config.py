from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Closet Loop API"
    app_version: str = "0.1.0"
    app_env: str = Field(default="development", alias="APP_ENV")
    port: int = Field(default=8000, alias="PORT")
    cors_allowed_origins: list[str] = Field(
        default=["http://localhost:3000"],
        alias="CORS_ALLOWED_ORIGINS",
    )

    # Supabase
    supabase_url: str = Field(default="", alias="SUPABASE_URL")
    supabase_anon_key: str = Field(default="", alias="SUPABASE_ANON_KEY")
    supabase_service_role_key: str = Field(default="", alias="SUPABASE_SERVICE_ROLE_KEY")
    worker_database_url: str = Field(default="", alias="WORKER_DATABASE_URL")

    # Storage buckets & TTLs
    storage_bucket_wardrobe: str = Field(default="wardrobe-media", alias="STORAGE_BUCKET_WARDROBE")
    storage_bucket_exports: str = Field(default="account-exports", alias="STORAGE_BUCKET_EXPORTS")
    signed_upload_ttl_seconds: int = Field(default=600, alias="SIGNED_UPLOAD_TTL_SECONDS")
    signed_read_ttl_seconds: int = Field(default=300, alias="SIGNED_READ_TTL_SECONDS")
    data_export_ttl_hours: int = Field(default=24, alias="DATA_EXPORT_TTL_HOURS")

    # Image & AI Limits
    image_max_bytes: int = Field(default=10 * 1024 * 1024, alias="IMAGE_MAX_BYTES")
    image_max_pixels: int = Field(default=25_000_000, alias="IMAGE_MAX_PIXELS")
    image_max_dimension: int = Field(default=2048, alias="IMAGE_MAX_DIMENSION")
    image_thumbnail_size: int = Field(default=400, alias="IMAGE_THUMBNAIL_SIZE")
    image_concurrency_limit: int = Field(default=4, alias="IMAGE_CONCURRENCY_LIMIT")

    ai_provider: str = Field(default="photoroom", alias="AI_PROVIDER")
    ai_api_key: str = Field(default="", alias="AI_API_KEY")
    ai_timeout_seconds: float = Field(default=20.0, alias="AI_TIMEOUT_SECONDS")
    ai_daily_quota_per_user: int = Field(default=10, alias="AI_DAILY_QUOTA_PER_USER")

    # Policy & consent versions
    current_terms_version: str = Field(default="2026-11", alias="CURRENT_TERMS_VERSION")
    current_privacy_version: str = Field(default="2026-11", alias="CURRENT_PRIVACY_VERSION")
    current_ai_policy_version: str = Field(
        default="2026-11-photoroom", alias="CURRENT_AI_POLICY_VERSION"
    )
    current_analytics_policy_version: str = Field(
        default="2026-11", alias="CURRENT_ANALYTICS_POLICY_VERSION"
    )

    support_daily_limit_per_user: int = Field(default=5, alias="SUPPORT_DAILY_LIMIT_PER_USER")


@lru_cache
def get_settings() -> Settings:
    return Settings()

