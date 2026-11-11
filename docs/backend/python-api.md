# Closet Loop — Backend Python và API

[Mục lục](../README.md) · Cập nhật: 11/11/2026

**Python là ngôn ngữ backend đã chốt.** FastAPI, Pydantic, Uvicorn và uv là lựa chọn triển khai đề xuất.

## Trách nhiệm

- Cung cấp REST API `/api/v1` cho frontend/mobile.
- Xác thực token, kiểm tra quyền đối tượng, validate request và trả các trường được phép.
- Điều phối nghiệp vụ, dùng Supabase theo JWT người gọi và RPC cho transaction.
- Cấp quyền upload, quản lý asset/job, gọi Rust và nhà cung cấp AI.
- Chạy quy trình dọn dữ liệu/xóa tài khoản có trạng thái bền vững.
- Quản lý bootstrap/onboarding, hồ sơ/cài đặt/chấp thuận, bản xuất JSON, thông báo và yêu cầu hỗ trợ; không giao các nghiệp vụ này cho Rust.

## Cấu trúc Python

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                   # FastAPI app, lifecycle, middleware
│   ├── api/
│   │   └── v1/router.py          # Ghép router dưới /api/v1
│   ├── core/
│   │   ├── config.py             # Môi trường, origin, timeout/quota
│   │   ├── errors.py             # Mã lỗi và exception handler
│   │   └── logging.py            # Log không chứa ảnh/token/secret
│   ├── infrastructure/
│   │   ├── supabase/client.py    # Client theo JWT, client đặc quyền hẹp
│   │   ├── ai/background_removal.py
│   │   └── native/image_core.py  # Adapter gọi Rust qua PyO3
│   └── modules/
│       ├── auth/                 # Current user và dependency xác thực
│       ├── accounts/             # Bootstrap, hồ sơ, chấp thuận, xóa
│       ├── settings/             # Tùy chọn, version và analytics
│       ├── data_exports/         # Yêu cầu JSON, snapshot, tải riêng
│       ├── notifications/        # Hộp thông báo và mark-read
│       ├── support/              # Tiếp nhận/đọc phiếu của chủ
│       ├── wardrobe/             # Món, tìm/lọc, trạng thái
│       ├── outfits/              # Bố cục outfit và version
│       ├── planner/              # Lịch, snapshot, wear log RPC
│       ├── insights/             # CPW và số lượt mặc
│       ├── media/                # Upload, finalize, URL đọc
│       ├── image_jobs/           # Job AI, timeout, quota
│       └── health/               # Liveness/readiness
├── scripts/
│   ├── cleanup_media.py
│   ├── process_account_deletions.py
│   ├── process_data_exports.py
│   ├── cleanup_retention.py
│   └── export_openapi.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── api/
├── pyproject.toml
└── uv.lock
```

Các thư mục package Python thêm `__init__.py` theo cấu hình package đã chọn. Chỉ tạo phần được triển khai.

## Bên trong một module

```text
app/modules/wardrobe/
├── __init__.py
├── router.py                     # HTTP path, method và dependency
├── service.py                    # Nghiệp vụ và điều phối
├── repository.py                 # Supabase và RPC
└── schemas.py                    # Pydantic request/response
```

| File | Trách nhiệm |
| --- | --- |
| `router.py` | Nhận params/query/body đã validate, lấy current user, gọi service |
| `service.py` | Nghiệp vụ; dùng service/hàm công khai của module khác |
| `repository.py` | Dữ liệu theo JWT, RPC và ánh xạ lỗi database |
| `schemas.py` | Pydantic request/response riêng; không dùng raw DB row làm API |

Module `auth` dùng `dependencies.py`, `service.py`, `schemas.py`; Supabase Auth quản lý đăng nhập/mật khẩu. Module nhỏ chỉ tạo file cần dùng. FastAPI hỗ trợ chia module bằng APIRouter và dependency. [Hướng dẫn](https://fastapi.tiangolo.com/tutorial/bigger-applications/).

## I/O và hợp đồng

- Dùng client I/O async khi phù hợp; lời gọi SDK đồng bộ và Rust xử lý ảnh chạy trong threadpool có giới hạn để tránh chặn event loop. [Async trong FastAPI](https://fastapi.tiangolo.com/async/).
- Tạo context/client Supabase theo request; không giữ session mutable dùng chung giữa người dùng. [Supabase Python](https://supabase.com/docs/reference/python/initializing).
- Route và schema Pydantic là nguồn sinh OpenAPI. Xuất `backend/openapi.json` để frontend sinh/đối chiếu type. [OpenAPI](https://fastapi.tiangolo.com/features/).
- `core/errors.py` chuẩn hóa lỗi HTTP/validation; lỗi validation dùng HTTP 422 theo hợp đồng API.
- Script dọn/xóa chạy theo lịch host, đọc trạng thái database và nhận việc có khóa để tránh xử lý trùng.
- Bản xuất dùng transaction `READ ONLY, REPEATABLE READ`. Worker Python có kết nối PostgreSQL server giới hạn quyền và truy vấn whitelist theo owner; không ghép nhiều request REST độc lập thành một snapshot. Cấu hình kết nối chỉ ở worker/backend.

## Đọc tiếp

- [Rust xử lý ảnh](rust-xu-ly-anh.md)
- [Xác thực](xac-thuc-va-phan-quyen.md)
- [Hợp đồng API](../api/hop-dong.md)
- [Tài khoản và cài đặt](tai-khoan-va-cai-dat.md)
- [Thông báo và hỗ trợ](thong-bao-va-ho-tro.md)
