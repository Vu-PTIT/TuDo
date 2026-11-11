# Closet Loop — Phạm vi và lộ trình

[Mục lục](../README.md) · Cập nhật: 11/11/2026

## Phạm vi và lộ trình

| Phân hệ | Giai đoạn 1: Core MVP | Giai đoạn tiếp theo |
| --- | --- | --- |
| Tài khoản | Đăng ký/xác minh/đăng nhập/khôi phục, đổi email/mật khẩu, đăng xuất thiết bị này/mọi thiết bị | Social login, MFA người dùng và quản lý từng thiết bị nếu cần |
| Hồ sơ và cài đặt | Onboarding bỏ qua được, tên/múi giờ, chế độ lịch, tùy chọn thông báo/đo lường | Theme/ngôn ngữ mới khi có nội dung và giao diện tương ứng |
| Quyền riêng tư và hỗ trợ | Chính sách công khai, tải JSON, xóa tài khoản, FAQ, gửi/xem yêu cầu hỗ trợ | Xuất kèm toàn bộ file ảnh, hội thoại hỗ trợ trong app nếu cần |
| Thông báo | Email Auth và hộp thông báo bản xuất trong app | Nhắc lịch giai đoạn 2; push khi có kế hoạch riêng |
| Digital Wardrobe | Thêm ảnh một món, sửa/xóa, phân loại thủ công, tìm/lọc, trạng thái sử dụng | AI gợi ý loại và thuộc tính ở giai đoạn 2 |
| Zero-Effort Input | Placeholder, thử tách nền ảnh một món, lưu ảnh gốc nếu AI lỗi | Screenshot Import và thử nghiệm Mirror Selfie Extract ở giai đoạn 2 |
| Outfit Studio | Chọn món, kéo thả, đổi kích thước, đổi lớp trước/sau, đặt tên và lưu | Gửi đề xuất cho bạn ở giai đoạn 3 |
| Outfit Planner | Lịch tuần/tháng, nhiều outfit/ngày, sự kiện, xác nhận/hủy xác nhận đã mặc | Nhắc lịch tự động ở giai đoạn 2 |
| Girl Math | Số món, số outfit, số lượt mặc, Cost-Per-Wear từng món | Đồ ngủ quên 90 ngày, xu hướng tuần/tháng ở giai đoạn 2 |
| Bestie Closet | Chưa mở trong MVP | Kết bạn, cấp quyền theo món và thời hạn, phối hộ ở giai đoạn 3 |
| Public Pass Closet | Chưa mở trong MVP | Tủ pass công khai, chia sẻ link, liên hệ Facebook/Zalo ở giai đoạn 4 |
| Personalization | Chưa mở trong MVP | Gợi ý theo phong cách, lịch trình, thời tiết; app mobile và widget ở giai đoạn 5 |

### Ranh giới MVP

- Chưa có thanh toán, đơn hàng, giao hàng, niêm yết giá pass hoặc thu phí giao dịch.
- Chưa có chat thời gian thực, bảng tin công khai, virtual try-on hoặc mô phỏng cơ thể.
- Nhập một ảnh nhiều món, đọc dữ liệu screenshot và tách quần áo trên người là các bài toán AI riêng, không coi là khả năng mặc định của tách nền.
- Chưa cam kết hoạt động ngoại tuyến hay push notification. Nhắc lịch là hạng mục sau MVP.
- Tách nền cơ bản thuộc phạm vi MVP; khi chưa cấu hình được nhà cung cấp, bản nội bộ vẫn dùng nhập ảnh thủ công. Chỉ coi hạng mục AI hoàn tất sau khi tích hợp và kiểm tra bằng ảnh thật.

## Quy tắc cho các giai đoạn sau

| Phân hệ | Quy tắc phải giữ |
| --- | --- |
| 90-Day Sunset | Tính từ ngày mặc gần nhất; chưa từng mặc thì tính từ ngày thêm vào tủ. Đủ 90 ngày mới gợi ý; không tự chuyển trạng thái hay công khai |
| Screenshot Import | Nhập ảnh do người dùng cung cấp; AI đề xuất và người dùng sửa. Không mặc định thu thập dữ liệu từ Shopee/TikTok Shop |
| Mirror Selfie Extract | Là thử nghiệm nhận diện/tách nhiều món; phải kiểm tra chất lượng với ảnh thật. Không hứa phục dựng chính xác phần quần áo bị che |
| Quyền Bestie | Cấp theo danh sách món, người nhận và thời điểm hết hạn. Thu hồi chặn truy cập mới ngay; bản ảnh đã tải trước đó không thể bảo đảm thu hồi |
| Đề xuất từ bạn | Không sửa đồ gốc. Khi chủ tủ lưu, kiểm tra lại quyền và các món còn hợp lệ; lưu lịch sử tác giả |
| Tủ Pass | Chỉ xuất bản sau xác nhận rõ ràng; xem trước đúng ảnh và thông tin sẽ công khai |
| Thông tin công khai | Tên món, ảnh được chọn, size, tình trạng, ghi chú pass và liên hệ được chủ tủ cho phép; loại bỏ giá mua/lịch sử/ghi chú riêng |
| Đã pass | Ẩn khỏi danh sách đang pass; giữ lịch sử riêng, cảnh báo các outfit/lịch sắp tới có dùng món đó |

Giai đoạn Public Pass chỉ mở sau khi chủ dự án rà soát yêu cầu pháp lý áp dụng cho cách vận hành thực tế tại Việt Nam. Tài liệu này không kết luận về nghĩa vụ pháp lý.

## Tiêu chí hoàn thành MVP

- [ ] Người mới tự đăng ký và thêm được ít nhất một món bằng ảnh và một placeholder.
- [ ] Tạo, lưu, mở lại và sửa outfit trên điện thoại lẫn máy tính.
- [ ] Lên lịch nhiều outfit cùng ngày; xác nhận và hủy xác nhận không đếm trùng.
- [ ] CPW xử lý đúng thiếu giá, giá 0, chưa mặc và các món xuất hiện ở nhiều outfit trong một ngày.
- [ ] AI cơ bản được kiểm tra bằng ảnh thực tế; lỗi AI không chặn việc lưu món thủ công.
- [ ] Dữ liệu và ảnh riêng không truy cập được bằng tài khoản khác hoặc khi chưa đăng nhập.
- [ ] Không có món nào bị công khai qua thao tác thống kê hay trạng thái sử dụng.
- [ ] Có trạng thái trống, đang tải, lỗi, thử lại và cảnh báo mất thay đổi ở nơi cần thiết.
- [ ] Có thể dùng các thao tác chính bằng bàn phím; bố cục hoạt động từ màn hình rộng 360 px.
- [ ] Có quy trình khôi phục dữ liệu vận hành và luồng xóa tài khoản đã kiểm chứng.
- [ ] Cài đặt/hồ sơ đồng bộ, tải JSON đúng chủ, có hỗ trợ nhận được phiếu; email Auth dùng hạ tầng gửi production.
- [ ] Hoàn thành [điều kiện ra mắt](../trien-khai/san-sang-ra-mat.md), gồm chính sách thật và người phụ trách vận hành.

## Đọc tiếp

- [Chức năng MVP](chuc-nang-mvp.md)
- [Kế hoạch code](../trien-khai/ke-hoach-code.md)
