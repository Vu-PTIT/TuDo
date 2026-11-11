# Closet Loop — Kinh doanh và đo lường

[Mục lục](../README.md) · Cập nhật: 11/11/2026

## Mô hình kinh doanh và đo lường

### Định hướng kinh doanh

- Freemium: quản lý tủ và vòng lặp mặc đồ cơ bản.
- Premium dự kiến: AI nâng cao, cá nhân hóa, thống kê sâu; chưa chốt mức giá hoặc hạn mức.
- Kiểm chứng chi phí xử lý ảnh trước khi đưa ra hạn mức miễn phí.
- Không dựa vào phí giao dịch pass trong giai đoạn đầu.

### Sự kiện và chỉ số cần theo dõi

| Chỉ số | Định nghĩa đề xuất |
| --- | --- |
| Kích hoạt | Tài khoản có ít nhất 3 món, 1 outfit và 1 mục lịch trong 7 ngày sau đăng ký |
| Thời gian đến giá trị đầu tiên | Từ lúc hoàn thành đăng ký đến lúc lưu outfit đầu tiên |
| Duy trì D7 | Người dùng thực hiện ít nhất một hành động chính vào ngày thứ 7 sau ngày đăng ký, tính theo múi giờ tài khoản |
| Sử dụng Planner | Số tài khoản xác nhận mặc ít nhất một lần mỗi tuần |
| Chất lượng nhập đồ | Tỉ lệ lưu thành công theo nguồn ảnh, placeholder và AI |
| Chất lượng AI | Tỉ lệ lỗi, thời gian xử lý, tỉ lệ người dùng chọn ảnh đã tách nền |

Hành động chính: thêm món, lưu outfit, thêm lịch hoặc xác nhận đã mặc. Sự kiện tối thiểu: `item_created`, `outfit_saved`, `planner_entry_created`, `wear_confirmed`, `wear_unconfirmed`, `image_processing_finished`.

Chưa đặt mục tiêu phần trăm khi chưa có dữ liệu thử nghiệm. Không đưa ảnh, nội dung ghi chú, token hoặc đường dẫn ảnh riêng tư vào công cụ đo lường.

Sự kiện phân tích hành vi chỉ gửi khi `analytics_opt_in = true`; mặc định tắt và ngừng gửi khi thu hồi. Báo cáo activation/D7 phải ghi rõ mẫu có chấp thuận, không suy thành toàn bộ người dùng. Log lỗi/quota kỹ thuật tối thiểu phục vụ vận hành được tách về mục đích và chính sách lưu; không dùng để âm thầm dựng lại hồ sơ hành vi. CPW/lịch sử mặc của chính chủ vẫn tính bình thường vì là chức năng sản phẩm.

## Đọc tiếp

- [Tổng quan](tong-quan.md)
