from contextvars import ContextVar
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")


def get_request_id() -> str:
    rid = request_id_ctx.get()
    if not rid:
        rid = str(uuid4())
        request_id_ctx.set(rid)
    return rid


class FieldErrorItem(BaseModel):
    field: str
    message: str


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str
    field_errors: list[FieldErrorItem] | None = None
    details: dict[str, Any] | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


class DataResponse[T](BaseModel):
    data: T


class PaginatedMeta(BaseModel):
    next_cursor: str | None = None
    has_more: bool = False
    total: int | None = None


class PaginatedDataResponse[T](BaseModel):
    data: list[T]
    meta: PaginatedMeta


class AppError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        field_errors: list[FieldErrorItem] | None = None,
        details: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.field_errors = field_errors
        self.details = details
        self.headers = headers or {}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(_request: Request, exc: AppError) -> JSONResponse:
        rid = get_request_id()
        headers = dict(exc.headers)
        headers["X-Request-ID"] = rid
        payload = ErrorResponse(
            error=ErrorDetail(
                code=exc.code,
                message=exc.message,
                request_id=rid,
                field_errors=exc.field_errors,
                details=exc.details,
            )
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=payload.model_dump(exclude_none=True),
            headers=headers,
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        rid = get_request_id()
        field_errors: list[FieldErrorItem] = []
        for err in exc.errors():
            loc = [str(part) for part in err.get("loc", []) if part != "body"]
            field_name = ".".join(loc) if loc else "request"
            field_errors.append(
                FieldErrorItem(field=field_name, message=err.get("msg", "Invalid value"))
            )
        payload = ErrorResponse(
            error=ErrorDetail(
                code="VALIDATION_ERROR",
                message="Dữ liệu gửi lên không hợp lệ.",
                request_id=rid,
                field_errors=field_errors,
            )
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=payload.model_dump(exclude_none=True),
            headers={"X-Request-ID": rid},
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_request: Request, _exc: Exception) -> JSONResponse:
        rid = get_request_id()
        payload = ErrorResponse(
            error=ErrorDetail(
                code="INTERNAL_ERROR",
                message="Đã xảy ra lỗi hệ thống. Vui lòng thử lại sau.",
                request_id=rid,
            )
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=payload.model_dump(exclude_none=True),
            headers={"X-Request-ID": rid},
        )

