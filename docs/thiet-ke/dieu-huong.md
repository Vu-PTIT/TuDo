# Closet Loop — Điều hướng và responsive

[Mục lục](../README.md) · Cập nhật: 11/11/2026

## Bản đồ màn hình

| Màn hình | Mục đích | Thao tác chính | Giai đoạn |
| --- | --- | --- | --- |
| Đăng ký/đăng nhập/khôi phục | Vào tài khoản | Tạo tài khoản, xác minh, đăng nhập | MVP |
| Bắt đầu | Đưa người mới đến giá trị đầu tiên | Thêm món hoặc placeholder | MVP |
| Hôm nay | Xem đồ đã chuẩn bị và việc cần làm | Mở outfit hôm nay, xác nhận đã mặc | MVP |
| Tủ đồ | Quản lý toàn bộ món | Tìm/lọc, thêm món, mở chi tiết | MVP |
| Thêm/sửa món | Số hóa và cập nhật đồ | Tải ảnh, xem tách nền, lưu thông tin | MVP |
| Chi tiết món | Hiểu một món và lịch sử của nó | Sửa, thêm vào Studio, xem CPW | MVP |
| Outfit đã lưu | Tìm lại các bộ đồ | Mở, sửa, lên lịch | MVP |
| Outfit Studio | Tạo/chỉnh outfit | Chọn, sắp xếp và lưu | MVP |
| Lịch mặc | Chuẩn bị và ghi nhận | Thêm outfit, đã mặc, bỏ qua | MVP |
| Girl Math | Xem mức độ sử dụng | Xem CPW và mở chi tiết món | MVP |
| Hồ sơ/cài đặt | Quản lý tài khoản | Hồ sơ, bảo mật, tùy chọn, tải/xóa dữ liệu | MVP |
| Thông báo | Kết quả công việc nền | Đọc, đánh dấu, mở trang xử lý | MVP |
| Trợ giúp/yêu cầu hỗ trợ | Tìm hướng dẫn, báo vấn đề | Đọc FAQ, gửi và xem trạng thái phiếu | MVP |
| Điều khoản/quyền riêng tư/giới thiệu | Thông tin dịch vụ công khai | Đọc chính sách, xem đầu mối và phiên bản | MVP |
| Bestie và quyền chia sẻ | Nhờ bạn phối đồ | Mời, chọn món, thu hồi quyền | Giai đoạn 3 |
| Đề xuất từ bạn | Duyệt outfit được gửi | Xem, phản hồi, lưu, lên lịch | Giai đoạn 3 |
| Tủ Pass của tôi/trang công khai | Chia sẻ món muốn pass | Xuất bản, ẩn, liên hệ bên ngoài | Giai đoạn 4 |

Xem [bố cục màn hình](bo-cuc-man-hinh.md) và [Outfit Studio](outfit-studio.md).

## Điều hướng và responsive

### Điều hướng MVP

| Nhãn hiển thị | URL | Vai trò |
| --- | --- | --- |
| Bắt đầu | `/` | Khách thấy giới thiệu ngắn + Đăng ký/Đăng nhập; đã có phiên hợp lệ thì kiểm tra hồ sơ và vào ứng dụng |
| Hôm nay | `/today` | Điểm vào sau đăng nhập |
| Tủ đồ | `/wardrobe` | Quản lý món |
| Outfit | `/outfits` | Các bộ đã lưu; mở Studio từ đây |
| Tạo outfit | `/outfits/new` | Studio tạo mới |
| Chỉnh outfit | `/outfits/[id]/edit` | Studio chỉnh sửa |
| Lịch mặc | `/planner` | Kế hoạch và ghi nhận |
| Girl Math | `/insights` | Thống kê |
| Cài đặt | `/settings` | Mục lục hồ sơ, bảo mật, tùy chọn, thông báo, dữ liệu |
| Hồ sơ/Bảo mật | `/settings/profile`, `/settings/security` | Sửa tên/múi giờ, đổi email/mật khẩu, đăng xuất |
| Tùy chọn/Thông báo | `/settings/preferences`, `/settings/notifications` | Chế độ lịch, thông báo hoạt động |
| Quyền riêng tư | `/settings/privacy` | Consent, analytics, bản xuất JSON, xóa tài khoản |
| Hộp thông báo | `/notifications` | Từ nút chuông trên header |
| Trợ giúp | `/help` | FAQ và kênh liên hệ công khai |
| Gửi/xem hỗ trợ | `/help/contact`, `/help/requests`, `/help/requests/[id]` | Form và phiếu của mình, cần đăng nhập |
| Chính sách/giới thiệu | `/terms`, `/privacy`, `/about` | Mở được khi chưa đăng nhập |

Chi tiết món dùng `/wardrobe/[id]`, thêm món dùng `/wardrobe/new`. Bestie và Tủ Pass chỉ xuất hiện khi đã triển khai; không đặt mục điều hướng chưa dùng được trong MVP.

Trang `/` công khai chỉ cần giới thiệu công dụng bằng nội dung thật, CTA vào tài khoản và link trợ giúp/chính sách. Không công bố số người dùng, đánh giá hoặc chứng nhận giả. Route Auth/onboarding có bản đồ riêng ở [bố cục tài khoản](tai-khoan.md).

### Quy tắc bố cục

| Chiều rộng | Shell | Nội dung |
| --- | --- | --- |
| 360–639 px | Header gọn; bottom navigation 5 mục | Padding 16 px; tủ đồ 2 cột; bộ lọc và chọn món mở sheet |
| 640–1023 px | Header/menu gọn; vẫn ưu tiên thao tác chạm | Padding 24 px; tủ đồ 3–4 cột theo chiều rộng thực |
| Từ 1024 px | Sidebar 224 px, header nội dung | Padding 32 px; tủ đồ 4–6 cột; Studio nhiều vùng |

Bottom navigation: **Hôm nay · Tủ đồ · Outfit · Lịch · Girl Math**. Cài đặt mở qua avatar, thông báo qua chuông; thêm món bằng nút rõ trong Tủ đồ. Chừa vùng safe-area và khoảng trống dưới nội dung để thanh điều hướng không che nút.

Giới hạn nội dung trang khoảng 1.440 px; Studio được dùng chiều rộng lớn hơn nếu có. Không kéo lưới trang phục quá rộng làm ảnh khó quan sát.

## Đọc tiếp

- [Bố cục](bo-cuc-man-hinh.md)
- [Studio](outfit-studio.md)
- [Tài khoản và onboarding](tai-khoan.md)
- [Cài đặt và hồ sơ](cai-dat-va-ho-so.md)
- [Thông báo và hỗ trợ](thong-bao-va-ho-tro.md)
