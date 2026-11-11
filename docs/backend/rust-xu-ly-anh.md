# Closet Loop — Backend Rust xử lý ảnh

[Mục lục](../README.md) · Cập nhật: 11/11/2026

**Rust là ngôn ngữ backend đã chốt.** Vai trò đề xuất trong MVP: thư viện native xử lý ảnh được Python gọi qua **PyO3**, build bằng **maturin**.

## Trách nhiệm

- Kiểm tra định dạng từ nội dung, đọc kích thước trước khi cấp phát ảnh lớn.
- Decode JPG/PNG/WebP theo cấu hình hỗ trợ; giới hạn input 10 MB và 25 megapixel.
- Chuẩn hóa hướng ảnh, encode lại ảnh sạch không mang metadata nguồn và tạo thumbnail.
- Giữ alpha của ảnh tách nền; trả bytes, kích thước và định dạng hợp lệ cho Python.
- Python quản lý quyền, Storage, database, quota, AI và trạng thái job.

Crate `image` hỗ trợ decode/encode và thao tác ảnh; cần kiểm tra codec, orientation và metadata bằng ảnh mẫu khi triển khai. [Tài liệu crate](https://docs.rs/image/latest/image/).

## Cấu trúc Rust

```text
backend/rust/image_core/
├── Cargo.toml
├── Cargo.lock
├── pyproject.toml                # Build-system maturin
├── src/
│   ├── lib.rs                    # Entry point PyO3
│   ├── decode.rs                 # Nhận diện, decode, orientation
│   ├── limits.rs                 # Giới hạn byte/pixel/alloc/output
│   ├── transform.rs              # Resize và thumbnail
│   ├── encode.rs                 # Output sạch, alpha và định dạng
│   └── errors.rs                 # Mã lỗi native có kiểm soát
└── tests/
    ├── input_validation.rs
    └── image_transform.rs
```

## Giao tiếp Python–Rust

Tên import Python đề xuất: `closet_loop_image_core`. Entry point PyO3 và cấu hình thư viện dùng cùng tên; Python gọi qua `app/infrastructure/native/image_core.py`.

| Giao diện đề xuất | Đầu vào | Kết quả |
| --- | --- | --- |
| `normalize_image` | Bytes ảnh, giới hạn decode/output | Bytes ảnh sạch và thumbnail, width/height, format |
| `validate_cutout` | Bytes ảnh từ AI, giới hạn | Ảnh hợp lệ có alpha và metadata dựng preview |

- Python truyền bytes và tùy chọn xử lý; Rust không nhận URL/path tùy ý hay token/database client.
- Giới hạn bộ nhớ và output; input sai phải trả lỗi có mã thay vì panic/unwrap.
- Adapter Python ánh xạ lỗi sang `INVALID_IMAGE`, `IMAGE_TOO_LARGE`, `UNSUPPORTED_FORMAT`.
- Đoạn Rust thuần giải phóng GIL khi phù hợp; Python dùng pool có giới hạn và giới hạn số ảnh đồng thời.
- Timeout coroutine không bảo đảm dừng thread/native đang chạy. Giới hạn decode/alloc và theo dõi tác vụ đến khi kết thúc vẫn bắt buộc.

PyO3 tạo Python extension từ Rust; maturin đóng gói wheel và hỗ trợ môi trường phát triển. [PyO3](https://pyo3.rs/), [maturin](https://www.maturin.rs/).

## Build và kiểm tra khi code

- Chốt CPython, Rust toolchain, PyO3/maturin tương thích; pin phiên bản và commit lockfile.
- Build wheel đúng OS/CPU/Python ABI của backend; cài vào runtime và kiểm tra import trong CI/readiness.
- Docker backend có stage build Rust và runtime Python chứa wheel; hai ngôn ngữ được phát hành cùng backend artifact.
- cargo test cho lõi ảnh, pytest integration cho adapter; kiểm tra ảnh lỗi/quá lớn, orientation, metadata và alpha.

## Đọc tiếp

- [Upload và AI](upload-va-ai.md)
- [Môi trường và build](../trien-khai/moi-truong.md)
