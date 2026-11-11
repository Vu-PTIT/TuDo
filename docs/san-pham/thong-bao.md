# Closet Loop — Thông báo

[Mục lục](../README.md) · Cập nhật: 11/11/2026

## Kênh và phạm vi

| Loại | Kênh bản ra mắt | Người dùng có tắt được? |
| --- | --- | --- |
| Xác minh email, khôi phục mật khẩu, xác nhận đổi email | Email do Auth gửi | Không có công tắc trong ứng dụng; gửi khi người dùng thực hiện thao tác |
| Bản sao dữ liệu sẵn sàng/thất bại | Hộp thông báo trong ứng dụng | Có; trạng thái vẫn xem tại trang Quyền riêng tư |
| Đã nhận yêu cầu hỗ trợ | Xác nhận tại form, lưu trong danh sách yêu cầu | Không phát thêm thông báo trùng chỉ để xác nhận |
| Kết quả xử lý ảnh | Hiện tại màn hình thêm món/job | Chưa cần một thông báo nền riêng cho luồng xử lý ngắn |
| Nhắc lịch mặc | Giai đoạn 2, phải chốt kênh và giờ nhắc trước khi làm | Opt-in khi triển khai |
| Quảng cáo, push Web/mobile | Chưa có trong bản ra mắt | Không hỏi quyền trình duyệt khi chưa có tính năng |

## Hộp thông báo trong ứng dụng

- Nút chuông trên header, có tên truy cập và số chưa đọc; mở `/notifications`.
- Danh sách phân trang mới nhất trước: tiêu đề, nội dung ngắn, thời điểm, đã/chưa đọc và liên kết tới đúng trang xử lý.
- Có **Đánh dấu đã đọc** từng mục và **Đánh dấu tất cả đã đọc**; mở chi tiết không tự thực hiện thao tác thay người dùng.
- Không có thông báo: “Bạn chưa có thông báo mới”. Tải lỗi có nút thử lại.
- Liên kết đích chỉ là route nội bộ được server cho phép; không nhận HTML hoặc URL tùy ý từ payload.
- Thông báo còn lưu không đồng nghĩa file xuất còn tồn tại; mở bản xuất hết hạn phải giải thích và cho yêu cầu lại.
- Đề xuất lưu 90 ngày rồi dọn tự động; thông báo không thay thế lịch sử mặc hay trạng thái nghiệp vụ.

## Quy tắc gửi

- Chỉ tạo thông báo khi trạng thái công việc đã commit; retry cùng sự kiện không tạo bản sao.
- Đọc cài đặt mới nhất khi tạo thông báo. Tắt thông báo chặn các mục hoạt động mới; các mục cũ vẫn đọc/đánh dấu được.
- Nội dung không chứa token, signed URL, giá mua hoặc ảnh tủ riêng. File xuất được mở qua trang yêu cầu xác thực.
- Email Auth dùng tên Closet Loop, tiếng Việt, domain gửi được xác minh và liên kết HTTPS đúng môi trường.
- Không báo “đã nhận email” khi mới gửi yêu cầu; hiển thị “Đã yêu cầu gửi email” và hướng dẫn kiểm tra thư rác/thử lại.

## Đọc tiếp

- [Cài đặt](cai-dat.md)
- [Backend thông báo và hỗ trợ](../backend/thong-bao-va-ho-tro.md)
- [Vận hành email](../trien-khai/email-va-tac-vu-nen.md)
