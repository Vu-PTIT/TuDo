# Closet Loop — Cấu trúc repository

[Mục lục](../README.md) · Cập nhật: 11/11/2026

Đây là cấu trúc dự kiến khi bắt đầu code. Bộ tài liệu hiện tại được tổ chức trong `docs/`.

## Các phần cấp repository

```text
project-root/
├── docs/                         # Mục lục và tài liệu theo chủ đề
├── frontend/                     # Next.js + TypeScript
│   ├── src/
│   ├── public/
│   ├── tests/
│   ├── package.json
│   ├── package-lock.json
│   └── .env.example
├── backend/                      # Python API và Rust native
│   ├── app/                      # FastAPI, nghiệp vụ, repository
│   ├── rust/image_core/          # Crate Rust và cấu hình maturin
│   ├── supabase/                 # Migration, RLS, RPC và seed
│   ├── scripts/                  # Worker xuất JSON, dọn/xóa dữ liệu
│   ├── tests/
│   ├── openapi.json              # Sinh từ FastAPI khi có mã nguồn
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── .python-version
│   ├── rust-toolchain.toml
│   ├── .env.example
│   └── Dockerfile
└── .gitignore
```

Frontend có lockfile theo package manager được chọn; cây trên minh họa npm. Python quản lý dependency trong pyproject/uv.lock; Rust trong Cargo.toml/Cargo.lock.

## Chia theo chức năng

| Chức năng | Frontend feature | Module Python | Dữ liệu quản lý |
| --- | --- | --- | --- |
| Tài khoản/session | `auth`, `accounts` | `auth`, `accounts` | profiles, consent, yêu cầu xóa; danh tính trên Supabase Auth |
| Cài đặt | `settings` | `settings` | user_settings; version và thay đổi analytics |
| Bản sao dữ liệu | `data-exports` | `data_exports` | data_export_requests và file private |
| Thông báo | `notifications` | `notifications` | notifications; event key chống lặp |
| Hỗ trợ | `support` | `support` | support_requests; audit chỉ dành cho vận hành |
| Hôm nay | `today` | Dùng API planner/outfits | Tổng hợp dữ liệu hiện có |
| Tủ đồ | `wardrobe` | `wardrobe` | wardrobe_items |
| Outfit Studio | `outfits` | `outfits` | outfits, outfit_items |
| Lịch mặc | `planner` | `planner` | planner_entries, wear_logs, wear_log_items |
| Girl Math | `insights` | `insights` | Truy vấn lượt mặc và giá mua; không giữ bộ đếm riêng |
| Ảnh/AI | `media` | `media`, `image_jobs` | media_assets, image_jobs; Python gọi Rust để xử lý bytes |

Bestie và Public Pass bổ sung feature frontend, module Python và migration khi đến giai đoạn tương ứng. Mobile thêm ở `mobile/`.

## Quy tắc phụ thuộc

```text
Frontend: app/page → feature component/hook → feature api → HTTP client
                                                            │
                                         HTTPS /api/v1 + token
                                                            │
Python:   auth dependency → Pydantic → router → service → repository
                                                   │         │
                                              Rust native    Supabase/RPC
```

- Frontend và backend thống nhất qua OpenAPI sinh từ FastAPI; mỗi phần có cấu hình, build và kiểm thử riêng.
- Frontend không import mã backend. Type HTTP được sinh/đối chiếu từ OpenAPI, không đưa raw database row sang UI.
- Page ghép component; router nhận/trả HTTP; service điều phối nghiệp vụ; repository truy vấn dữ liệu.
- Module dùng service/hàm công khai của module khác; không sửa bảng của module khác để né quy tắc nghiệp vụ.
- Transaction quan trọng nằm trong RPC; service gọi một transaction cho xác nhận mặc.
- Khi đổi API, cập nhật schema Pydantic, sinh lại `backend/openapi.json` và cập nhật lớp `api/`/type frontend trong cùng thay đổi.
- Rust được gọi qua adapter Python, nhận dữ liệu ảnh và trả kết quả có schema; ranh giới thư viện không mang quyền truy cập người dùng.

## Đọc tiếp

- [Frontend](../frontend/cau-truc.md)
- [Python API](../backend/python-api.md)
- [Rust xử lý ảnh](../backend/rust-xu-ly-anh.md)
