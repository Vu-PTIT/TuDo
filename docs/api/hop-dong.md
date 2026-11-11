# Closet Loop — Hợp đồng HTTP API

[Mục lục](../README.md) · Cập nhật: 11/11/2026

## Hợp đồng API giữa frontend và backend

Toàn bộ endpoint nghiệp vụ do **backend FastAPI** cung cấp với tiền tố **`/api/v1`**. Đường dẫn trong bảng là phần sau tiền tố này. Frontend đặt hàm gọi tương ứng ở `features/<tên>/api/`; hợp đồng sinh từ route/Pydantic và xuất thành `backend/openapi.json` khi triển khai.

### Hợp đồng theo chức năng

- [Tài khoản, hồ sơ, cài đặt và bản sao dữ liệu](tai-khoan-va-cai-dat.md).
- [Thông báo và hỗ trợ](thong-bao-va-ho-tro.md).
- Bảng dưới là endpoint tủ đồ, outfit, lịch, ảnh và thống kê. Các file cùng dùng quy ước HTTP trong tài liệu này.

### Endpoint nghiệp vụ cốt lõi

| Module | Method và đường dẫn | Nội dung và kiểm tra chính |
| --- | --- | --- |
| `wardrobe` | `GET /wardrobe/items`, `GET /wardrobe/items/:id` | Danh sách/chi tiết riêng; danh sách hỗ trợ tìm, lọc và phân trang |
| `wardrobe` | `POST /wardrobe/items`, `PATCH /wardrobe/items/:id` | Tạo/sửa món từ ảnh hoặc placeholder; xác minh asset/bản ảnh cùng chủ |
| `wardrobe` | `DELETE /wardrobe/items/:id` | Xóa mềm; lịch/outfit nhận trạng thái món thiếu |
| `outfits` | `GET /outfits`, `GET /outfits/:id` | Đọc danh sách/chi tiết, bao gồm bố cục để dựng preview |
| `outfits` | `POST /outfits`, `PATCH /outfits/:id` | Lưu tên, món và bố cục trong transaction; khi sửa kiểm tra version |
| `outfits` | `DELETE /outfits/:id` | Xóa mềm outfit; snapshot lịch cũ vẫn được giữ |
| `planner` | `GET /planner/entries` | Đọc theo khoảng ngày có giới hạn; phục vụ lịch tuần/tháng và trang Hôm nay |
| `planner` | `POST /planner/entries` | Nhận outfit, ngày và sự kiện; backend tạo snapshot hợp lệ, trạng thái `planned` |
| `planner` | `PATCH /planner/entries/:id`, `DELETE /planner/entries/:id` | Kiểm tra expected version; mục đã mặc phải hủy xác nhận trước |
| `planner` | `POST /planner/entries/:id/confirm-wear` | Nhận `operation_key`, `expected_version`; gọi RPC transaction; trả trạng thái/version mới |
| `planner` | `POST /planner/entries/:id/unconfirm-wear` | Cùng cơ chế key/version; bỏ đúng đóng góp của mục lịch |
| `planner` | `POST /planner/entries/:id/skip` | Kiểm tra expected version; chỉ đổi mục chưa mặc, không tạo log |
| `insights` | `GET /insights/summary`, `GET /insights/cost-per-wear` | Trả số món/outfit/lượt mặc và CPW; xử lý thiếu giá/chưa mặc; danh sách CPW có phân trang |
| `media` | `POST /media/uploads` | Tạo asset staging và quyền upload đúng path; ghi thời hạn quyền upload |
| `media` | `POST /media/uploads/:id/finalize` | Kiểm tra file thực, chuẩn hóa, tạo thumbnail và đánh dấu ready |
| `media` | `POST /media/:id/read-url` | Xác minh quyền đọc và bản ảnh; trả URL ngắn hạn, không nhận path tùy ý |
| `media` | `GET /media/:id/download?variant=original\|cutout` | Kiểm tra chủ/bản ảnh hợp lệ rồi stream tải xuống; private/no-store, tên file an toàn; không nhận object path từ client |
| `image_jobs` | `POST /image-jobs`, `GET /image-jobs/:id` | Tạo job theo asset/request key hoặc xem job đúng chủ; quota và timeout ở backend |
| `health` | `GET /health` | Kiểm tra tiến trình hoạt động; không trả secret, token hay dữ liệu tài khoản |

Đăng ký, đăng nhập, xác minh email và khôi phục mật khẩu đi qua Supabase Auth; module `auth` backend xác thực token của API nghiệp vụ. Không tạo thêm kho mật khẩu trong backend.

### Quy ước request/response

- Request nghiệp vụ dùng JSON và Bearer token; file upload đi trực tiếp vào Storage bằng quyền backend cấp.
- Ngày dùng `YYYY-MM-DD`; timestamp dùng ISO 8601; giá dùng số nguyên VND hoặc `null`.
- Response thành công trả `data`; danh sách có thông tin phân trang. Backend chỉ trả trường được phép qua kiểu response, không trả raw row có trường nội bộ.
- Lỗi có `error.code`, thông báo và lỗi theo trường nếu phù hợp. Dùng mã ổn định như `VALIDATION_ERROR`, `UNAUTHENTICATED`, `NOT_FOUND`, `CONFLICT`, `QUOTA_EXCEEDED`, `IMAGE_PROCESSING_FAILED`; UI ánh xạ sang tiếng Việt.
- Ánh xạ HTTP tương ứng: 422 cho validation và 400 cho yêu cầu nghiệp vụ không hợp lệ, 401 cho xác thực, 404 cho tài nguyên không truy cập được, 409 cho version xung đột, 429 cho hạn mức. Không tiết lộ sự tồn tại của tài nguyên riêng cho người không có quyền.
- 403 cho trạng thái tài khoản đang xóa; 410 cho bản xuất của chính mình đã hết hạn; 503 cho bảo trì/lỗi dịch vụ tạm thời. Trả `Retry-After` khi có thời điểm thử lại đã xác định.
- Lỗi server có `request_id` để tra cứu; thông báo không chứa stack trace, token hoặc nội dung riêng. Download JSON/ảnh là response tập tin với Content-Type/Content-Disposition phù hợp, không dùng envelope `data`.
- Frontend không tự retry mutation có version/operation key bằng một ý định cũ sau khi đã nhận trạng thái mới; xử lý theo [quy tắc transaction](../database/transaction.md).

## Đọc tiếp

- [Python API](../backend/python-api.md)
- [Xác thực](../backend/xac-thuc-va-phan-quyen.md)
- [Transaction](../database/transaction.md)
