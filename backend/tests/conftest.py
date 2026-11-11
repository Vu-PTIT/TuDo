import io
from collections.abc import AsyncGenerator
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient
from PIL import Image

from app.infrastructure.supabase.client import (
    AuthUserRecord,
    TransactionalStore,
    get_store,
    utc_now,
)
from app.main import app


def make_test_image_bytes(
    width: int = 120,
    height: int = 160,
    fmt: str = "JPEG",
    rgba: bool = False,
) -> bytes:
    mode = "RGBA" if rgba else "RGB"
    color = (220, 80, 120, 200) if rgba else (220, 80, 120)
    img = Image.new(mode, (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


@pytest.fixture
def test_store() -> TransactionalStore:
    store = TransactionalStore()
    user_a_id = UUID("11111111-1111-1111-1111-111111111111")
    user_b_id = UUID("22222222-2222-2222-2222-222222222222")
    unverified_id = UUID("33333333-3333-3333-3333-333333333333")

    store.auth_users[user_a_id] = AuthUserRecord(
        id=user_a_id,
        email="alice@closetloop.test",
        email_confirmed_at=utc_now(),
        password="AliceSecretPassword123!",
    )
    store.tokens["token-user-a"] = user_a_id

    store.auth_users[user_b_id] = AuthUserRecord(
        id=user_b_id,
        email="bob@closetloop.test",
        email_confirmed_at=utc_now(),
        password="BobSecretPassword123!",
    )
    store.tokens["token-user-b"] = user_b_id

    store.auth_users[unverified_id] = AuthUserRecord(
        id=unverified_id,
        email="unverified@closetloop.test",
        email_confirmed_at=None,
        password="UnverifiedPassword123!",
    )
    store.tokens["token-unverified"] = unverified_id

    app.dependency_overrides[get_store] = lambda: store
    yield store
    app.dependency_overrides.clear()


@pytest.fixture
async def client(test_store: TransactionalStore) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest.fixture
def headers_a() -> dict[str, str]:
    return {"Authorization": "Bearer token-user-a"}


@pytest.fixture
def headers_b() -> dict[str, str]:
    return {"Authorization": "Bearer token-user-b"}


@pytest.fixture
def headers_unverified() -> dict[str, str]:
    return {"Authorization": "Bearer token-unverified"}
