# Closet Loop — Hướng dẫn bắt đầu và hồ sơ

[Mục lục](../README.md) · Cập nhật: 11/11/2026

## Lần đầu sử dụng

| Bước | Nội dung | Có thể bỏ qua? |
| --- | --- | --- |
| 1. Chào bạn | Tên hiển thị, múi giờ; giải thích tủ mặc định riêng tư | Có; dùng tên mặc định “Bạn” và múi giờ Việt Nam |
| 2. Món đầu tiên | Hai nút **Thêm bằng ảnh**, **Tạo thẻ tạm**; nói rõ ảnh AI là tùy chọn | Có; vào tủ trống vẫn dùng được |
| 3. Bắt đầu phối | Khi đã có món, gợi ý tạo outfit rồi lên lịch | Có; không bắt buộc hoàn thành mới vào ứng dụng |

- Hướng dẫn dùng chính dữ liệu thật của người dùng; không tự thêm quần áo demo vào tủ riêng.
- Lưu trạng thái đã hoàn thành/bỏ qua ở server để không hỏi lại trên từng thiết bị.
- Đăng xuất hoặc mất mạng giữa bước: giữ dữ liệu đã lưu, quay lại đúng trạng thái; không tạo lại món đầu tiên.
- Checklist ở Hôm nay: thêm món → tạo outfit → lên lịch; chỉ đánh dấu từ dữ liệu đã lưu, có thể đóng hướng dẫn.
- Không bắt nhập số điện thoại, địa chỉ, ngày sinh, số đo hay ảnh cơ thể để dùng chức năng cốt lõi.

## Hồ sơ cá nhân

| Trường | Quy tắc bản ra mắt |
| --- | --- |
| Tên hiển thị | 1–50 ký tự sau bỏ khoảng trắng đầu/cuối; không cần duy nhất |
| Email | Đọc từ Auth; đổi qua luồng bảo mật, không sửa bằng API hồ sơ |
| Múi giờ | Mặc định `Asia/Ho_Chi_Minh`; danh sách mã IANA hợp lệ, có tìm kiếm |
| Ảnh đại diện | Dùng chữ cái tên hiển thị; upload avatar để sau, tránh thêm một luồng ảnh chưa cần |
| Ngôn ngữ, tiền tệ | Tiếng Việt, VND ở bản ra mắt; hiển thị thông tin, chưa đưa công tắc chưa hoạt động |

## Đổi múi giờ

- Xem trước ngày/giờ hiện tại ở múi giờ mới và giải thích ảnh hưởng đến “Hôm nay”, ngày được phép xác nhận mặc.
- Ngày đã lên lịch và ngày đã mặc giữ nguyên dạng ngày địa phương đã ghi; không dịch lịch sử bằng số giờ chênh lệch.
- Sau lưu, tải lại Hôm nay, Planner và thống kê; backend tính giới hạn ngày theo hồ sơ đã cập nhật.
- Có xung đột với tab khác thì yêu cầu tải bản mới; không tự ghi đè.

## Tiêu chí nghiệm thu

- [ ] Người bỏ qua hướng dẫn vẫn thêm đồ, phối và lên lịch bình thường.
- [ ] Đăng nhập thiết bị khác giữ hồ sơ và trạng thái hướng dẫn.
- [ ] Đổi tên/múi giờ tồn tại sau tải lại; ngày lịch cũ không bị thay đổi.

## Đọc tiếp

- [Cài đặt](cai-dat.md)
- [API tài khoản](../api/tai-khoan-va-cai-dat.md)
