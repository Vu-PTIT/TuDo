# Closet Loop — Dữ liệu thông báo và hỗ trợ

[Mục lục](../README.md) · Cập nhật: 11/11/2026

## Schema

| Bảng | Trường chính | Ràng buộc |
| --- | --- | --- |
| `notifications` | `id`, `owner_id`, `event_key`, `type`, `title`, `body`, `target_type`, `target_id`, `read_at`, `created_at` | UNIQUE(owner_id, event_key); type/target theo danh sách cho phép |
| `support_requests` | `id`, `owner_id`, `reference_code`, `request_key`, `category`, `subject`, `description`, `diagnostics`, `status`, `created_at`, `updated_at`, `closed_at` | UNIQUE(owner_id, request_key), reference_code duy nhất; trạng thái received/in_review/closed |
| `support_audit_events` | `id`, `request_id`, `operator_id`, `action`, `created_at` | Chỉ vận hành đọc/ghi; không chứa nội dung phiếu hoặc thông tin đăng nhập |

- `diagnostics` là JSON theo schema whitelist, tối đa 2 KB; không nhận object tùy ý.
- Mã tham chiếu dễ đọc không phải bí mật xác thực; vẫn kiểm tra owner khi tra cứu.
- Index danh sách `(owner_id, created_at, id)`; partial index mục chưa đọc; index trạng thái/thời gian để nhân sự theo dõi phiếu tồn.

## RLS và transaction

- Mặc định cấm client INSERT/UPDATE/DELETE trực tiếp; chủ SELECT chỉ các trường được phép ở hai bảng đầu. Audit không công khai qua Data API.
- Tạo support request qua RPC: kiểm tra `auth.uid()`, tài khoản hoạt động, hạn mức, nội dung và request key trong cùng transaction.
- Người dùng không đổi `status`, owner hoặc diagnostics sau tiếp nhận. Quyền vận hành là đường riêng có xác thực, không lấy role từ user metadata tự sửa.
- Đọc notification theo owner; RPC đánh dấu đã đọc chỉ sửa `read_at`, idempotent. Mark-all dùng cutoff timestamp do server sinh.
- Cập nhật bản xuất + tạo notification chống lặp trong cùng transaction; kiểm tra settings và tombstone dưới khóa.
- Với `SECURITY DEFINER`: cố định search_path, thu hẹp EXECUTE và kiểm tra owner; xem [quy tắc RPC](transaction.md).

## Lưu và xóa

- Thông báo: đề xuất 90 ngày. Phiếu: đề xuất 90 ngày sau khi đóng; audit tối thiểu có thời hạn riêng phải công bố trước launch.
- Xóa tài khoản dọn thông báo, nội dung phiếu và diagnostics; gỡ liên hệ định danh trong audit theo chính sách, không xóa mất dấu cần thiết cho quá trình dọn đang chạy.
- Mã phiếu hoặc log audit không được trở thành bản sao của mô tả người dùng đã yêu cầu xóa.

## Đọc tiếp

- [Backend thông báo/hỗ trợ](../backend/thong-bao-va-ho-tro.md)
- [API thông báo/hỗ trợ](../api/thong-bao-va-ho-tro.md)
