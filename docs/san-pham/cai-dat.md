# Closet Loop — Cài đặt

[Mục lục](../README.md) · Cập nhật: 11/11/2026

Trang `/settings` là mục lục tài khoản; mỗi nhóm có trang con và liên kết trực tiếp. Vào qua avatar ở mọi màn hình chính.

## Nhóm cài đặt bản ra mắt

| Nhóm | Chức năng | URL |
| --- | --- | --- |
| Hồ sơ | Tên hiển thị, múi giờ; email chỉ đọc | `/settings/profile` |
| Tài khoản và bảo mật | Đổi email, đổi mật khẩu, đăng xuất thiết bị này/mọi thiết bị | `/settings/security` |
| Tùy chọn sử dụng | Lịch mặc mặc định tuần hoặc tháng | `/settings/preferences` |
| Thông báo | Bật/tắt thông báo hoạt động trong ứng dụng; giải thích email tài khoản | `/settings/notifications` |
| Quyền riêng tư và dữ liệu | Tải bản sao JSON, tùy chọn đo lường, xem chính sách, xóa tài khoản | `/settings/privacy` |
| Trợ giúp và giới thiệu | FAQ, gửi hỗ trợ, điều khoản, phiên bản ứng dụng | `/help`, `/about` |

## Giá trị mặc định

- Chế độ lịch: tuần; lịch bắt đầu thứ Hai ở bản đầu.
- Thông báo hoạt động trong ứng dụng: bật. Tắt không làm mất trạng thái job và yêu cầu hỗ trợ tại trang gốc.
- Đo lường hành vi tùy chọn: tắt. Bật/tắt lưu theo tài khoản; log kỹ thuật tối thiểu phục vụ vận hành được giải thích riêng.
- Tủ đồ luôn riêng tư ở MVP; không có công tắc “công khai toàn bộ tủ”.
- Chỉ có giao diện sáng, tiếng Việt và VND ở bản đầu. Thêm lựa chọn theme/ngôn ngữ khi đã có giao diện và nội dung tương ứng.

## Quy tắc lưu

- Form có nút **Lưu thay đổi**, hiển thị đang lưu, thành công hoặc lỗi ngay tại nhóm vừa sửa.
- Chưa thay đổi thì nút lưu không hoạt động. Rời form có chỉnh sửa thì xác nhận bỏ thay đổi.
- Lỗi mạng không mất giá trị đã nhập; chỉ cập nhật giao diện dùng chung sau khi server xác nhận.
- Hồ sơ và cài đặt có version riêng; hai thiết bị cùng sửa nhận xung đột rõ ràng.
- Mật khẩu không được lưu cùng cài đặt, không được khôi phục từ bản nháp form.
- Sau đăng xuất xóa state/cache riêng; khi đăng nhập tài khoản khác không được thấy hồ sơ/tủ cũ.

## Tiêu chí nghiệm thu

- [ ] Mở trực tiếp từng URL con được; tải lại không mất mục đang xem.
- [ ] Giá trị cài đặt đồng bộ giữa thiết bị sau khi tải lại; lỗi lưu và xung đột không báo thành công.
- [ ] Tùy chọn lịch có tác dụng thật khi mở Planner; không chỉ lưu một trường không được dùng.
- [ ] Không có nút cài đặt dẫn đến tính năng chưa triển khai.

## Đọc tiếp

- [Thông báo](thong-bao.md)
- [Quyền riêng tư](quyen-rieng-tu.md)
- [Bố cục cài đặt](../thiet-ke/cai-dat-va-ho-so.md)
