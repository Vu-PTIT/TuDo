# Closet Loop — Bố cục thông báo và hỗ trợ

[Mục lục](../README.md) · Cập nhật: 11/11/2026

## Hộp thông báo

- Header AppShell: nút chuông có nhãn “Thông báo, 2 mục chưa đọc” và avatar; không thêm tab thứ sáu ở bottom navigation.
- `/notifications`: tiêu đề → **Tất cả/Chưa đọc** → **Đánh dấu tất cả đã đọc** → danh sách phân trang.
- Mỗi dòng có tiêu đề, nội dung ngắn, thời điểm, dấu chưa đọc và hành động mở trang; cho đánh dấu đã đọc độc lập.
- Đích hết hạn/đã xóa: hiện giải thích ở trang đích và đường về, không hiện stack trace hoặc toast “không xác định” rồi bỏ người dùng lại.

## Trợ giúp

```text
Bạn cần giúp gì?
Tài khoản và email       >
Ảnh và tách nền          >
Tủ đồ, outfit và lịch    >
Lượt mặc và Girl Math    >
Quyền riêng tư, dữ liệu  >

[Gửi yêu cầu hỗ trợ] [Yêu cầu của tôi]
Kênh liên hệ công khai · Giờ hỗ trợ
```

- Người chưa đăng nhập vẫn đọc FAQ và kênh liên hệ. Nút gửi form hướng tới đăng nhập với đường quay lại hợp lệ.
- `/help/contact`: chủ đề → tiêu đề → mô tả → chẩn đoán tùy chọn có xem trước → **Gửi yêu cầu**.
- Cảnh báo ngắn cạnh mô tả: “Không gửi mật khẩu hoặc mã đăng nhập”. Không tự đính kèm ảnh tủ.
- Gửi xong hiện mã yêu cầu, trạng thái tiếp nhận và **Xem yêu cầu**; không hứa đã có nhân sự đọc ngay.
- `/help/requests`: danh sách của mình; `/help/requests/[id]`: nội dung đã gửi, trạng thái, thời gian, hướng dẫn phản hồi qua email.

## Trạng thái toàn ứng dụng

| Tình huống | Màn hình/hành động |
| --- | --- |
| Chưa đăng nhập/hết phiên | Về đăng nhập, giữ đường nội bộ quay lại; xóa dữ liệu riêng khỏi UI |
| Tài nguyên không có hoặc không được phép xem | Trang không tìm thấy và về khu vực chính; không tiết lộ tên/ảnh đối tượng |
| Mất mạng | Banner “Mất kết nối”, giữ form còn an toàn trong bộ nhớ; thử lại khi người dùng chọn |
| 429 | Nói thao tác đang bị giới hạn và thời gian thử lại nếu có; không retry vô hạn |
| 409 khi lưu | Giải thích dữ liệu đã thay đổi, cho tải bản mới; không ghi đè âm thầm |
| Lỗi server | Nội dung ngắn, request ID có thể sao chép, thử lại hoặc mở hỗ trợ |
| Bảo trì | Trang/banner thời gian dự kiến nếu đã xác định, kênh hỗ trợ; ngừng gửi mutation khi API báo bảo trì |

Các trang công khai dùng header/footer gọn; các trang thông báo/yêu cầu riêng dùng AppShell và bảo vệ đăng nhập. Không yêu cầu kết nối realtime hoặc offline để đáp ứng các trạng thái này.

## Đọc tiếp

- [Trợ giúp sản phẩm](../san-pham/ho-tro.md)
- [Component và state](../frontend/component-va-trang-thai.md)
