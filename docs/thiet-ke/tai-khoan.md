# Closet Loop — Bố cục tài khoản

[Mục lục](../README.md) · Cập nhật: 11/11/2026

## Khung trang xác thực

Desktop: khối giới thiệu thương hiệu khoảng 45% bên trái, form rộng tối đa 420 px bên phải. Mobile: logo → tiêu đề → form → liên kết phụ; không hiển thị ảnh lớn đẩy form khỏi màn hình đầu. Giữ nền tím nhạt, nút berry theo [hệ thống thiết kế](he-thong-thiet-ke.md).

```text
[Closet Loop]
Chào bạn, mở tủ đồ thôi
Email
[ban@example.com                 ]
Mật khẩu
[••••••••••••                Hiện]
                          Quên mật khẩu?
[             Đăng nhập          ]
Chưa có tài khoản? Đăng ký
Trợ giúp · Điều khoản · Quyền riêng tư
```

## Trang và trạng thái

| Route | Nội dung chính | Trạng thái cần có |
| --- | --- | --- |
| `/login` | Email, mật khẩu, hiện/ẩn, đăng nhập, quên mật khẩu | Sai thông tin, email chưa xác minh, đang gửi, mất mạng, bị giới hạn |
| `/register` | Email, mật khẩu, nhập lại, checkbox điều khoản, tạo tài khoản | Lỗi theo trường, mật khẩu chưa đạt, đang gửi, hướng dẫn kiểm tra email |
| `/verify-email` | Thông báo kiểm tra hộp thư, gửi lại, sửa email/quay lại | Chờ gửi, gửi lại bị giới hạn, link đã dùng/hết hạn |
| `/forgot-password` | Email và nút gửi hướng dẫn | Thông báo trung tính, lỗi gửi hoặc mất mạng |
| `/reset-password` | Mật khẩu mới + nhập lại | Đang kiểm tra phiên khôi phục, hợp lệ, link lỗi/hết hạn, thành công |
| `/auth/error` | Lý do có thể xử lý và hành động tiếp theo | Xác minh lại, yêu cầu link mới hoặc quay về đăng nhập |
| `/onboarding` | Tên/múi giờ, thêm món đầu tiên, gợi ý phối | Bỏ qua, lỗi lưu, quay lại hướng dẫn dở |

`/auth/confirm` là callback xử lý token/hash theo flow Auth, không phải trang sản phẩm để lưu hoặc hiển thị token. Kiểm tra loại tác vụ rồi chuyển tới đúng bước; `next` chỉ là đường dẫn nội bộ được cho phép.

## Hướng dẫn bắt đầu

```text
Chào bạn, mình bắt đầu nhé
Tên hiển thị [Bạn                ]
Múi giờ      [Việt Nam           ]
Tủ đồ của bạn chỉ mình bạn xem được.
[Tiếp tục]                 [Bỏ qua]

Thêm món đầu tiên
[Thêm bằng ảnh]  [Tạo thẻ tạm]
[Để sau]
```

- Tiến trình ngắn, không dùng thanh phần trăm giả. Bỏ qua đưa về Hôm nay với trạng thái trống có hành động rõ.
- Nếu thiếu chấp nhận điều khoản hợp lệ ở callback/thiết bị mới, hiển thị bước xác nhận trước khi gọi bootstrap; không tự tích chọn từ metadata.
- Tạo món dùng form Tủ đồ hiện có; không duy trì một bản form khác trong onboarding.

## Hành vi form

- Label luôn nhìn thấy; autocomplete phù hợp email/current-password/new-password; cho dán mật khẩu, nút hiện/ẩn có tên rõ.
- Lỗi liên kết với trường; lỗi toàn form đặt phía trên nút chính, được screen reader thông báo.
- Disable gửi lặp khi đang xử lý; chỉ hiện spinner thật. Không xóa email hoặc nội dung an toàn khi lỗi; không lưu mật khẩu vào bản nháp lâu dài.
- Link footer hoạt động cả khi chưa đăng nhập; bấm mở điều khoản không làm mất form đăng ký.

## Đọc tiếp

- [Nghiệp vụ tài khoản](../san-pham/tai-khoan-va-dang-nhap.md)
- [Điều hướng](dieu-huong.md)
