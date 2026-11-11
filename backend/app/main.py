from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_v1_router
from app.core.config import get_settings
from app.core.errors import register_exception_handlers, request_id_ctx
from app.core.logging import logger


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting Closet Loop Backend API")
    yield
    logger.info("Shutting down Closet Loop Backend API")


def create_app() -> FastAPI:
    cfg = get_settings()
    app = FastAPI(
        title=cfg.app_name,
        version=cfg.app_version,
        description="Closet Loop REST API (/api/v1) — Digital Wardrobe, Outfit Studio, Planner, and Girl Math",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.cors_allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        expose_headers=["Retry-After", "Content-Disposition", "X-Request-ID"],
    )

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
        incoming_rid = request.headers.get("X-Request-ID")
        rid = incoming_rid.strip() if incoming_rid and len(incoming_rid) <= 128 else str(uuid4())
        token = request_id_ctx.set(rid)
        try:
            response: Response = await call_next(request)
            response.headers["X-Request-ID"] = rid
            return response
        finally:
            request_id_ctx.reset(token)

    register_exception_handlers(app)
    app.include_router(api_v1_router)
    return app


app = create_app()

