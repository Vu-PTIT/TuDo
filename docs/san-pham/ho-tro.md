# Closet Loop — Trợ giúp và hỗ trợ

[Mục lục](../README.md) · Cập nhật: 11/11/2026

## Trung tâm trợ giúp

`/help` mở được khi chưa đăng nhập để người mất tài khoản vẫn tìm được cách liên hệ.

- Bài hướng dẫn ngắn: không nhận email, đặt lại mật khẩu, thêm ảnh/HEIC, dùng placeholder, tách nền lỗi, tạo outfit, cách tính CPW, tải/xóa dữ liệu.
- Phân nhóm và liên kết theo vấn đề; chưa cần công cụ tìm kiếm nếu mới có ít bài.
- Có kênh liên hệ thật do chủ dự án cấu hình và thời gian làm việc; không tự đặt địa chỉ email hoặc hứa thời gian phản hồi chưa có người trực.
- Người chưa đăng nhập dùng kênh liên hệ công khai. Form trong app yêu cầu đăng nhập để theo dõi đúng chủ yêu cầu.

## Gửi yêu cầu trong ứng dụng

| Trường | Quy tắc |
| --- | --- |
| Chủ đề | Tài khoản, ảnh/AI, tủ đồ, outfit/lịch, dữ liệu cá nhân, lỗi khác, góp ý |
| Tiêu đề | 5–120 ký tự |
| Mô tả | 20–4.000 ký tự; gợi ý bước thực hiện và kết quả mong đợi |
| Thông tin chẩn đoán | Mã lỗi/request ID, phiên bản, loại trình duyệt; cho xem trước, chỉ gửi nếu chọn |
| File đính kèm | Chưa hỗ trợ bản đầu; không yêu cầu gửi mật khẩu hoặc token |

- Nhấn gửi → chống gửi lặp → server trả mã yêu cầu → form xác nhận **Đã tiếp nhận**, kèm đường dẫn xem lại.
- Gửi lỗi thì giữ nội dung. Mất mạng sau gửi có thể thử lại cùng request key, không tạo hai phiếu.
- `/help/requests` hiển thị yêu cầu của chính tài khoản; chi tiết có thời gian và trạng thái `đã tiếp nhận/đang xem xét/đã đóng`.
- Phản hồi hỗ trợ qua email đã xác minh; bản đầu chưa có chat hoặc hộp hội thoại trong app.
- Địa chỉ trả lời lấy từ Auth tại lúc nhân sự chuẩn bị phản hồi, không tin email trong payload. Xác minh riêng trước các yêu cầu đổi danh tính hoặc cung cấp dữ liệu.

## Cách vận hành

- Có người được giao kiểm tra yêu cầu mới mỗi ngày làm việc; quyền đọc dữ liệu hỗ trợ giới hạn theo vai trò vận hành.
- Người trực dùng công cụ nội bộ được bảo vệ; không cần xây trang admin đầy đủ để ra mắt.
- Chỉ xem nội dung người dùng gửi; không mặc định mở cả tủ đồ khi xử lý phiếu.
- Đề xuất dọn nội dung phiếu 90 ngày sau khi đóng; phiếu chưa xử lý cần được theo dõi, không tự đóng để đạt chỉ số.

## Tiêu chí nghiệm thu

- [ ] Người chưa đăng nhập mở trợ giúp, điều khoản và chính sách được.
- [ ] Gửi/làm mới/gửi lại cùng thao tác không tạo phiếu trùng; tài khoản khác không đọc được phiếu.
- [ ] Yêu cầu thử trên staging được người trực tìm thấy và phản hồi qua kênh vận hành thật.

## Đọc tiếp

- [Bố cục thông báo và hỗ trợ](../thiet-ke/thong-bao-va-ho-tro.md)
- [API hỗ trợ](../api/thong-bao-va-ho-tro.md)
