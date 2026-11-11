# Closet Loop — API thông báo và hỗ trợ

[Mục lục](../README.md) · Cập nhật: 11/11/2026

Prefix **`/api/v1`**, Bearer token; lỗi, envelope và quyền theo [hợp đồng chung](hop-dong.md).

## Thông báo

| Method / đường dẫn | Hành vi |
| --- | --- |
| `GET /notifications` | Phân trang cursor; tùy chọn `unread_only`; mỗi mục có nội dung ngắn, route đích đã kiểm tra, read_at |
| `GET /notifications/unread-count` | Số mục chưa đọc của user hiện tại |
| `POST /notifications/:id/read` | Đánh dấu một mục đã đọc, idempotent |
| `POST /notifications/read-all` | Server đặt cutoff hiện tại, đánh dấu các mục tới cutoff; trả số mục vừa đổi và cutoff |

- Quyền sở hữu kiểm tra trước khi trả trạng thái; ID người khác trả 404.
- Mark-read không sửa nội dung thông báo và không thực hiện hành động ở trang đích.
- Mục đã được dọn có thể trả 404; frontend tải lại danh sách, không coi là lỗi mất toàn bộ dữ liệu.

## Hỗ trợ

| Method / đường dẫn | Hành vi |
| --- | --- |
| `POST /support/requests` | `request_key`, category, subject, description; diagnostics tùy chọn; 201 khi tạo, 200 khi trả lại cùng yêu cầu |
| `GET /support/requests` | Danh sách phiếu của mình, phân trang |
| `GET /support/requests/:id` | Nội dung người dùng gửi, trạng thái, thời gian, mã tham chiếu; không có ghi chú/audit nội bộ |

- Cùng request key nhưng nội dung khác → 409; dùng key mới khi người dùng chủ động gửi một phiếu khác.
- Độ dài theo [sản phẩm hỗ trợ](../san-pham/ho-tro.md); diagnostics theo schema whitelist. Thừa trường nhạy cảm bị từ chối, không âm thầm ghi nguyên payload.
- 429 khi vượt hạn mức, có `Retry-After` khi xác định được. Frontend giữ form và không tự gửi lại liên tục.
- Không có API cập nhật trạng thái cho user. Công cụ vận hành dùng đường riêng có quyền giới hạn.

## Nội dung không cần đăng nhập

FAQ, `/terms`, `/privacy`, `/about` là nội dung có phiên bản do frontend render từ nguồn được kiểm soát; chưa cần CMS hoặc API nội dung riêng. Trang trợ giúp công khai không truy vấn bảng phiếu.

## Đọc tiếp

- [Backend](../backend/thong-bao-va-ho-tro.md)
- [Dữ liệu](../database/thong-bao-va-ho-tro.md)
