# Closet Loop — Môi trường phát triển và build

[Mục lục](../README.md) · Cập nhật: 11/11/2026

Cấu hình/lệnh dưới đây áp dụng khi khởi tạo mã nguồn; hiện tại dự án đang chuẩn bị bằng tài liệu.

## Môi trường từng phần

| Phần | Local đề xuất | Công cụ/cấu hình |
| --- | --- | --- |
| Frontend | `http://localhost:3000` | Node phù hợp Next.js, package.json và lockfile |
| Python API | `http://localhost:8000` | CPython pin phiên bản, uv, pyproject.toml/uv.lock, Uvicorn |
| Rust extension | Trong tiến trình Python | Rust toolchain, Cargo.lock, PyO3/maturin; wheel đúng ABI/OS/CPU |
| Database/ảnh | Supabase local hoặc staging | Migration, RLS, RPC và Storage private |

## Biến môi trường

- Frontend: `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1`, URL/publishable key Supabase cho Auth.
- Backend: `PORT=8000`, allowlist origin frontend, URL/key Supabase, secret tác vụ đặc quyền, khóa AI, giới hạn ảnh, timeout/quota.
- Worker: kết nối PostgreSQL server giới hạn quyền cho snapshot xuất JSON; bucket `account-exports`, thời hạn file/hạn lưu, deadline, số retry, lease và lịch chạy. Không dùng chuỗi kết nối database trong frontend.
- Auth: SMTP/domain gửi, Site URL/redirect allowlist, mẫu email, chính sách mật khẩu/link và rate limit cấu hình riêng từng môi trường; các giá trị mật lưu tại dịch vụ hoặc secret store.
- Nội dung công khai: phiên bản điều khoản/privacy/thông báo AI, URL/kênh hỗ trợ thật và phiên bản phát hành. Không trộn secret vào cấu hình công khai.
- Rust nhận tùy chọn xử lý từ Python; secret và cấu hình tài khoản thuộc Python.
- Mỗi ứng dụng có `.env.example`. File môi trường thật không commit; secret backend không xuất hiện trong bundle frontend.

## Chạy và build

1. Frontend cài dependency và chạy từ `frontend/` bằng script npm được khai báo.
2. Backend tạo môi trường Python từ `backend/pyproject.toml` và `uv.lock`.
3. Build/cài extension bằng maturin vào đúng môi trường Python; kiểm tra `import closet_loop_image_core`.
4. Chạy API, ví dụ `uv run uvicorn app.main:app --reload --port 8000` từ `backend/` sau khi có mã nguồn.
5. Xuất OpenAPI từ FastAPI và cập nhật type/client frontend.

Wheel phát hành phải build cho nền tảng đích; readiness kiểm tra native import và cấu hình cần thiết. [Hướng dẫn maturin](https://www.maturin.rs/).

## CORS, I/O và tác vụ nền

- CORS khai báo đúng origin frontend, method, Authorization/Content-Type; backend nhận Bearer token. [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/).
- Cho phép browser đọc response headers bằng `expose_headers`: `Retry-After`, `Content-Disposition`, `X-Request-ID` nếu dùng. Đây là cấu hình riêng với request headers được cho phép; kiểm tra download/tên file và quota từ frontend khác origin.
- Giới hạn threadpool, concurrent image jobs và tài nguyên native; timeout I/O tách riêng với giới hạn decode ảnh.
- Worker xuất JSON và script cleanup/xóa tài khoản chạy theo lịch host, nhận việc có khóa/lease và tiếp tục sau gián đoạn; [chi tiết](email-va-tac-vu-nen.md).
- Tách local/staging/production; dữ liệu demo không chứa ảnh riêng của người dùng.

## Đọc tiếp

- [Python API](../backend/python-api.md)
- [Rust extension](../backend/rust-xu-ly-anh.md)
- [Phát hành](phat-hanh-va-van-hanh.md)
