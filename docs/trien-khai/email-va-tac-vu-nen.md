# Closet Loop — Email và tác vụ nền

[Mục lục](../README.md) · Cập nhật: 11/11/2026

## Email Auth trước production

- Cấu hình SMTP riêng, domain/tên gửi thật, xác thực domain theo nhà cung cấp và hộp thư hỗ trợ nhận được thư trả lời.
- Không dùng dịch vụ SMTP mặc định của Supabase cho production; dịch vụ mặc định có giới hạn người nhận/hạn mức và không được thiết kế cho vận hành thật. [Hướng dẫn SMTP](https://supabase.com/docs/guides/auth/auth-smtp).
- Template tiếng Việt cho xác minh, khôi phục, đổi email; link HTTPS đúng domain và đường dẫn từng môi trường.
- Site URL/redirect allowlist chính xác cho production; tránh wildcard rộng. Callback tự kiểm tra `next`, loại tác vụ và lỗi. [Redirect URL](https://supabase.com/docs/guides/auth/redirect-urls).
- Cấu hình thời hạn link, giới hạn gửi, mật khẩu và bảo vệ đổi email/mật khẩu; giá trị hiển thị trên UI phải bám cấu hình/lỗi thật, không đóng đinh hạn mức mặc định trong code.
- Tắt click tracking nếu làm hỏng link xác thực; thử bằng thư nhận thật, link bị dùng lại, trình quét email và liên kết mở ở trình duyệt khác. Không log URL chứa token/hash.
- Theo dõi lỗi gửi/bounce/hạn mức qua công cụ được bảo vệ của nhà cung cấp; không tuyên bố thư đã tới hộp thư chỉ vì API nhận yêu cầu.

## Tác vụ Python bền vững

Không cần thêm Redis/Celery ngay: dùng bảng yêu cầu trong PostgreSQL và tiến trình Python do nền tảng triển khai chạy theo lịch/worker. Bảng trạng thái là nguồn công việc, không dùng tác vụ giữ trong RAM sau response.

| Tác vụ | Nguồn công việc | Nhịp chạy đề xuất ban đầu |
| --- | --- | --- |
| Xuất JSON | `data_export_requests` | Worker/lịch mỗi phút; UI không hứa xử lý ngay |
| Xóa tài khoản | `account_deletion_requests` | Lịch mỗi phút, tiếp tục được sau gián đoạn |
| Dọn ảnh bỏ dở/file xuất hết hạn | Asset/manifest/hạn lưu | Mỗi giờ, theo lô có giới hạn |
| Dọn thông báo/phiếu đã quá hạn lưu | Timestamp/trạng thái theo chính sách | Hằng ngày |

- Nhận việc bằng transaction khóa hàng (`SKIP LOCKED`) + lease/attempt token; gia hạn nếu cần, chỉ worker còn token hợp lệ được commit kết quả. Khóa chỉ dùng nhận việc hàng đợi, không dùng để xuất dữ liệu người dùng. [PostgreSQL locking clause](https://www.postgresql.org/docs/current/sql-select.html#SQL-FOR-UPDATE-SHARE).
- Từng lần xử lý có deadline và I/O timeout; worker dừng được khi quá hạn. Worker cũ không ghi đè kết quả của worker mới, output mỗi attempt dùng path riêng và được GC.
- Retry giới hạn, có backoff và lỗi công khai; hết số lần chuyển failed và cảnh báo người trực. Không retry vô hạn hoặc lặp việc gọi AI có phí.
- Ưu tiên tombstone xóa: hủy việc chờ và kiểm tra trước/sau tạo output; chỉ báo xóa hoàn tất sau khi worker đang chạy đã dừng và quét cuối không còn output ghi muộn.
- Theo dõi tuổi việc lâu nhất, số lần retry, lần chạy dọn gần nhất. Khi scheduler ngừng, có cảnh báo và lệnh chạy lại được ghi trong runbook.
- Chốt cadence, tài nguyên, deadline và lưu dữ liệu theo hosting thực tế trước beta; đây là giá trị khởi đầu, chưa phải SLA.

## Ranh giới AI

Job AI MVP vẫn là request ngắn có giới hạn ở [pipeline ảnh](../backend/upload-va-ai.md); worker trên phục vụ bản xuất/dọn dữ liệu. Nếu chuyển AI sang nền sau này, cần trạng thái durable, quota và idempotency của nhà cung cấp, không chỉ đưa một coroutine vào background.

## Đọc tiếp

- [Môi trường](moi-truong.md)
- [Sẵn sàng ra mắt](san-sang-ra-mat.md)
