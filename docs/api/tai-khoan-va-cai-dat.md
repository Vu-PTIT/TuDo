# Closet Loop — API tài khoản và cài đặt

[Mục lục](../README.md) · Cập nhật: 11/11/2026

Endpoint dưới prefix **`/api/v1`**, tuân theo [quy ước HTTP chung](hop-dong.md). Trừ nội dung chính sách tĩnh, mọi endpoint dưới đây cần Bearer token hợp lệ.

## Danh tính và hồ sơ

| Method / đường dẫn | Request chính | Kết quả |
| --- | --- | --- |
| `POST /accounts/bootstrap` | `terms_version`, `privacy_version`, `accept_terms: true`, `acknowledge_privacy: true` | 201 khi khởi tạo, 200 khi đã có; cùng owner không tạo lặp |
| `GET /accounts/me` | Không | Hồ sơ + version, email từ Auth, email đang chờ xác minh nếu có, trạng thái tài khoản |
| `PATCH /accounts/me` | `display_name` và/hoặc `timezone`, `expected_version` | Hồ sơ đã cập nhật + version mới |
| `POST /accounts/me/onboarding` | `action: complete` hoặc `skip` | Trạng thái hướng dẫn; server đặt timestamp, cùng action là idempotent |
| `DELETE /accounts/me` | `current_password`, `confirmation: XÓA TÀI KHOẢN`, `request_key` | 202 đã tiếp nhận + mã tham chiếu; chưa khẳng định dọn xong |

- `/accounts/me` chưa bootstrap trả `404 PROFILE_NOT_READY`; frontend gọi bootstrap sau khi có chấp nhận hợp lệ. Không tự tạo lại khi thấy 404 ở mọi endpoint.
- Bootstrap chỉ cho user đã xác minh email; thiếu chấp nhận/phiên bản chính sách cũ trả `400 POLICY_ACCEPTANCE_REQUIRED` với phiên bản cần hiển thị.
- `account_status` chỉ là response suy ra từ trạng thái server: `active`/`deleting`; client không được PATCH.
- Tài khoản đang xóa: cấm mutation mới với `403 ACCOUNT_DELETION_PENDING`; request xóa đã tiếp nhận cùng key trả lại biên nhận nếu phiên vẫn còn hợp lệ.
- Request nhạy cảm không được ghi body vào log/APM. Chỉ server kiểm tra mật khẩu khi xóa; không tạo endpoint tự quản lý password hash.

## Settings và chấp thuận

| Method / đường dẫn | Request chính | Kết quả |
| --- | --- | --- |
| `GET /settings` | Không | `planner_default_view`, `activity_notifications`, `analytics_opt_in`, version |
| `PATCH /settings` | Trường cần sửa + `expected_version` | Settings/version mới; 409 nếu bản cũ |
| `GET /accounts/me/consents` | Phân trang cursor | Các sự kiện chấp thuận/chính sách của chủ tài khoản |
| `POST /accounts/me/consents` | `kind`, `policy_version`, `action`, `request_key`, `expected_revision` | Sự kiện/biên nhận và trạng thái hiện hành; 409 nếu revision cũ, retry cùng key không áp lại ý định |

Loại/action cho phép: terms/accepted, privacy/acknowledged, ai/accepted hoặc withdrawn. Terms/privacy lần đầu được ghi ở bootstrap, endpoint consent dùng khi cần ghi nhận phiên bản mới; analytics chỉ đổi qua PATCH settings và ghi sự kiện cùng transaction. Revision khởi đầu 0 khi chưa có sự kiện. Server phát hành nội dung/phiên bản chính sách và AI qua cấu hình công khai, không chứa secret; không nhận loại hoặc phiên bản tùy ý.

## Bản sao dữ liệu

| Method / đường dẫn | Hành vi |
| --- | --- |
| `POST /data-exports` | Body `request_key`; 202 nhận việc hoặc trả yêu cầu cũ cùng key; giới hạn tần suất ở server |
| `GET /data-exports` | Danh sách của chính mình, phân trang, mới nhất trước |
| `GET /data-exports/:id` | Trạng thái, snapshot_at, expires_at, lỗi công khai; không trả object path/lease |
| `GET /data-exports/:id/download` | Stream JSON riêng tư; 409 chưa sẵn sàng, 410 hết hạn, 404 không có quyền |

Download là ngoại lệ của envelope JSON `data`: thành công trả tập tin với header tải xuống; thất bại vẫn dùng cấu trúc lỗi chung. Request không cùng chủ luôn trả 404, kể cả khi file đã hết hạn.

## Auth không đi qua Python API nghiệp vụ

Đăng ký/đăng nhập, gửi lại xác minh, khôi phục, đổi email/mật khẩu và đăng xuất dùng SDK Supabase Auth. Callback frontend chỉ chấp nhận loại tác vụ và URL quay lại nằm trong allowlist; không chuyển token sang query của trang sản phẩm. [Luồng mật khẩu](https://supabase.com/docs/guides/auth/passwords), [redirect URL](https://supabase.com/docs/guides/auth/redirect-urls).

## Đọc tiếp

- [Backend tài khoản](../backend/tai-khoan-va-cai-dat.md)
- [Dữ liệu tài khoản](../database/tai-khoan-va-cai-dat.md)
