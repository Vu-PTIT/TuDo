# Closet Loop — Bố cục cài đặt và hồ sơ

[Mục lục](../README.md) · Cập nhật: 11/11/2026

## Trang mục lục cài đặt

```text
Cài đặt
[B] Bạn
    ban@example.com

Hồ sơ                         >
Tài khoản và bảo mật           >
Tùy chọn sử dụng               >
Thông báo                     >
Quyền riêng tư và dữ liệu      >
Trợ giúp và giới thiệu         >

[Đăng xuất thiết bị này]
```

- Desktop: menu nhóm rộng khoảng 240 px bên trái, nội dung form bên phải, form tối đa 640 px.
- Mobile: danh sách nhóm → trang con có nút quay về Cài đặt; mỗi trang con có URL riêng.
- Nhóm đang mở có dấu chọn rõ bằng chữ/icon; trang bảo mật không hiện ô mật khẩu đã điền từ trạng thái trước.

## Hồ sơ, tùy chọn và thông báo

- Hồ sơ: chữ cái đại diện → tên → email chỉ đọc + **Đổi email** → múi giờ + xem trước “Hôm nay” → **Lưu thay đổi**.
- Tùy chọn: lựa chọn Lịch tuần/Lịch tháng có nhãn và mô tả ngắn; không bày công tắc theme/ngôn ngữ chưa hoạt động.
- Thông báo: công tắc thông báo hoạt động, giải thích email tài khoản riêng; liên kết tới Hộp thông báo.
- Lưu thành công báo tại form, đồng thời cập nhật tên trên header. Xung đột giữ nội dung người dùng đang nhập để họ so với bản mới.

## Bảo mật

| Khối | Bố cục/hành vi |
| --- | --- |
| Email | Email hiện tại, email đang chờ nếu có, nút đổi; form nhập email mới và hướng dẫn xác minh |
| Mật khẩu | Mật khẩu hiện tại, mới, nhập lại; điều kiện rõ trước khi gửi, xử lý bước xác thực bổ sung |
| Phiên đăng nhập | Hai nút phân biệt “Đăng xuất thiết bị này”, “Đăng xuất mọi thiết bị”; lựa chọn thứ hai có xác nhận |

## Quyền riêng tư và dữ liệu

```text
Quyền riêng tư và dữ liệu
Tủ đồ của bạn đang ở chế độ riêng tư.

Đo lường sử dụng tùy chọn      [Tắt]
[Lưu thay đổi]

Bản sao dữ liệu (JSON, không kèm ảnh)
[Yêu cầu bản sao] / Đang chuẩn bị / [Tải JSON]
Chuẩn bị lúc ... · Hết hạn lúc ...

Chấp thuận xử lý AI            [Xem/Thu hồi]
Chính sách quyền riêng tư      >
Điều khoản sử dụng             >

Xóa tài khoản
Giải thích phạm vi và việc không thể khôi phục.
[Yêu cầu xóa tài khoản]
```

- Vùng xóa tách ở cuối bằng khoảng cách và mô tả; nút phá hủy không đặt cạnh nút lưu thông thường.
- Form xóa: danh sách sẽ xóa → nhắc bản xuất → mật khẩu → nhập **XÓA TÀI KHOẢN** → xác nhận. Có **Hủy** trước khi tiếp nhận.
- Sau 202: trang biên nhận “Đã tiếp nhận yêu cầu”, mã tham chiếu, hướng dẫn liên hệ; kết thúc phiên. Không dùng màn hình thành công khẳng định đã dọn xong.
- Bản xuất hết hạn/lỗi: có lý do công khai và nút yêu cầu lại theo quota; đang chờ không cho tạo thêm một hàng đợi mới.

## Đọc tiếp

- [Cài đặt sản phẩm](../san-pham/cai-dat.md)
- [Quyền riêng tư](../san-pham/quyen-rieng-tu.md)
