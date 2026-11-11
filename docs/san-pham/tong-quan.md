# Closet Loop — Tổng quan sản phẩm

[Mục lục](../README.md) · Cập nhật: 11/11/2026

Nguồn: bản tổng quan do chủ dự án cung cấp. Các quy tắc chi tiết là đề xuất triển khai, chưa phải kết quả nghiên cứu người dùng.

## Tổng quan

| Nội dung | Định nghĩa |
| --- | --- |
| Tên | Closet Loop |
| Slogan | Your Closet, Your Style, Your Story. |
| Sản phẩm | Tủ quần áo số, phối outfit, lên lịch mặc và kết nối bạn thân |
| Người dùng chính | Nữ 18–30 tuổi, sinh viên, người mới đi làm và người yêu thời trang |
| Giá trị hằng ngày | Biết mình có gì, phối được nhiều bộ hơn và chuẩn bị trước việc mặc đồ |
| Giá trị dài hạn | Hiểu mức độ sử dụng quần áo, nhận gợi ý từ bạn bè, pass những món không dùng |
| Tính cách | Thông minh, vui vẻ, gần gũi; tôn trọng quyền riêng tư |

**Tuyên bố sản phẩm:** Closet Loop giúp người dùng biến quần áo đang sở hữu thành một tủ đồ dễ tìm, dễ phối và dễ sử dụng mỗi ngày.

## Vấn đề và kết quả mong muốn

| Vấn đề | Kết quả người dùng cần |
| --- | --- |
| Có nhiều quần áo nhưng không biết mặc gì | Nhìn được toàn bộ tủ và tạo outfit từ đồ sẵn có |
| Mất thời gian chọn đồ | Chuẩn bị outfit cho ngày hoặc sự kiện sắp tới |
| Ngại nhập từng món | Thêm bằng ảnh hoặc thẻ tạm với ít trường bắt buộc |
| Quên món đã mua, không biết có dùng hiệu quả không | Xem lịch sử mặc và chi phí mỗi lần mặc |
| Nhờ bạn phối đồ qua tin nhắn bất tiện | Cho bạn xem đúng những món được chia sẻ và gửi outfit đề xuất |
| Chuẩn bị bài pass tốn công | Tái sử dụng ảnh, thông tin có sẵn để tạo tủ pass riêng |

### Vai trò

| Vai trò | Quyền chính | Giai đoạn |
| --- | --- | --- |
| Chủ tủ | Quản lý đồ, outfit, lịch, thống kê và quyền chia sẻ của mình | MVP |
| Người chưa đăng nhập | Xem giới thiệu, FAQ, điều khoản, chính sách; tạo/khôi phục tài khoản | MVP |
| Bạn thân được mời | Xem các món được cấp quyền, tạo và gửi đề xuất | Giai đoạn 3 |
| Khách xem tủ pass | Xem thông tin công khai và mở liên hệ bên ngoài | Giai đoạn 4 |

Quyền vận hành hệ thống là quyền nội bộ. MVP không cần xây một giao diện quản trị riêng.

Nền tảng khi ra mắt gồm [tài khoản](tai-khoan-va-dang-nhap.md), [hồ sơ](bat-dau-va-ho-so.md), [cài đặt](cai-dat.md), [thông báo](thong-bao.md), [quyền riêng tư](quyen-rieng-tu.md) và [hỗ trợ](ho-tro.md), bên cạnh vòng lặp tủ đồ cốt lõi.

## Nguyên tắc sản phẩm

1. Tủ đồ, lịch và giá mua mặc định riêng tư.
2. AI đưa ra kết quả để người dùng xác nhận; người dùng luôn sửa hoặc nhập thủ công được.
3. Lên lịch không đồng nghĩa với đã mặc. Chỉ thao tác xác nhận thực tế mới tạo dữ liệu sử dụng.
4. Placeholder là món đồ sử dụng được trong Studio và Planner, không phải dữ liệu mẫu.
5. Không tự công khai hoặc tự pass món đồ vì ít sử dụng.
6. Bestie Closet phục vụ phối đồ từ tủ số; không cho mượn hay cho thuê đồ thực tế.
7. Giao diện ưu tiên ảnh quần áo và thao tác hằng ngày; thống kê dùng lời dễ hiểu, không gây áp lực chi tiêu.

## Đọc tiếp

- [Phạm vi](pham-vi-va-lo-trinh.md)
- [Quyết định](quyet-dinh.md)
