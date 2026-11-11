# Closet Loop — Backend thông báo và hỗ trợ

[Mục lục](../README.md) · Cập nhật: 11/11/2026

## Module `notifications`

- Tạo thông báo trạng thái bản xuất trong cùng transaction cập nhật trạng thái yêu cầu; `event_key` duy nhất theo chủ để chống lặp.
- Đọc cài đặt thông báo mới nhất trong transaction. Không tạo khi đã tắt hoặc tài khoản đang xóa.
- API chỉ cho chủ tài khoản đọc và đánh dấu đã đọc. Client không được tạo thông báo, sửa tiêu đề/đích hoặc tự đổi owner.
- Nội dung được dựng từ template/loại sự kiện cho phép. Đích là enum route + mã đối tượng; không lưu HTML/URL tùy ý.
- Đánh dấu một mục idempotent; đánh dấu tất cả chỉ áp dụng mục đã tồn tại tới thời điểm server nhận thao tác, không đánh dấu thông báo đến sau.
- Danh sách phân trang cursor, giới hạn trang; đếm chưa đọc bằng truy vấn đúng owner, không cần WebSocket ở bản đầu.
- Frontend tải khi mở app/hộp thông báo và refresh có kiểm soát khi quay lại tab. Không polling dày trên tab nền.

## Module `support`

1. Kiểm tra tài khoản còn hoạt động, validate chủ đề/độ dài, lọc trường chẩn đoán cho phép.
2. Lấy owner từ JWT; ghi yêu cầu với `request_key`, trả mã tham chiếu an toàn để hiển thị.
3. Cùng key + cùng nội dung trả lại bản ghi cũ; cùng key + nội dung khác trả `409 CONFLICT`.
4. Người dùng đọc danh sách/chi tiết của chính mình; trạng thái ban đầu `received`, chỉ vận hành đổi `in_review`/`closed`.

- Hạn mức đề xuất 5 yêu cầu/ngày/tài khoản, kết hợp giới hạn theo IP ở cổng API; phản hồi 429 và `Retry-After` khi xác định được.
- Chẩn đoán chỉ nhận `request_id`, mã lỗi, phiên bản, nhóm trình duyệt; không nhận nguyên stack trace, cookie, URL kèm query, ảnh hoặc nội dung form nghiệp vụ.
- Nội dung là plain text, escape khi hiển thị và khi đưa vào công cụ nội bộ. Không dùng mô tả người dùng làm mã lệnh hoặc template thực thi.
- Không gắn email trong bảng phiếu nếu chưa cần. Khi xử lý, công cụ được bảo vệ tra email hiện tại từ Auth theo ID đã kiểm chứng; không tự cung cấp quyền đọc toàn tủ cho nhân sự hỗ trợ.
- Tạo phiếu là hoàn tất việc tiếp nhận ở hệ thống; bản ra mắt chưa gửi email xác nhận phiếu hoặc xây chat. Nhân sự phản hồi qua hộp thư hỗ trợ được cấu hình.

## Quyền vận hành

- Công cụ người trực phải đăng nhập bằng danh tính vận hành riêng có MFA; không đưa service key cho trình duyệt hoặc cho phép user tự đặt role qua metadata.
- Quyền quản trị qua môi trường server/công cụ được bảo vệ, chỉ thao tác phiếu được giao và ghi audit tối thiểu cho việc xem/đổi trạng thái.
- Không thêm endpoint admin vào API công khai nếu chưa có cơ chế xác thực/phân quyền cho nó. MVP có thể dùng công cụ nội bộ có kiểm soát thay portal admin tự xây.
- Audit không ghi nội dung phiếu, token hoặc ảnh; việc lưu/xóa audit tuân theo chính sách vận hành đã công bố.

## Đọc tiếp

- [Schema thông báo và hỗ trợ](../database/thong-bao-va-ho-tro.md)
- [Hợp đồng API](../api/thong-bao-va-ho-tro.md)
