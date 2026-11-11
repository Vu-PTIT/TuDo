# Closet Loop — Điều kiện sẵn sàng ra mắt

[Mục lục](../README.md) · Cập nhật: 11/11/2026

Đây là danh sách công việc bắt buộc kiểm tra khi xây ứng dụng thật. Các ô chưa đánh dấu không có nghĩa đã triển khai hoặc đã kiểm thử.

## Tài khoản và trải nghiệm hoàn chỉnh

- [ ] Đăng ký, xác minh, khôi phục, đổi mật khẩu/email và đăng xuất chạy bằng email thật trên domain staging/production tương ứng.
- [ ] Có onboarding bỏ qua được, hồ sơ và cài đặt có tác dụng thật, đồng bộ sau tải lại.
- [ ] Có hộp thông báo, trợ giúp công khai, form hỗ trợ, trang điều khoản/quyền riêng tư và đầu mối vận hành thật.
- [ ] Người mới thực hiện trọn vòng thêm món → phối → lên lịch → ghi nhận mặc → xem CPW trên điện thoại và máy tính.
- [ ] Có trạng thái mất phiên, lỗi mạng, 404, conflict, quota, bảo trì; nội dung lỗi có đường xử lý.

## Dữ liệu và quyền riêng tư

- [ ] RLS/RPC/Storage được kiểm tra hai tài khoản và truy cập trực tiếp API/Data API; frontend ẩn nút không phải cơ chế phân quyền.
- [ ] Tải JSON đúng chủ, snapshot nhất quán, tải lại/hết hạn được; nội dung không có secret/path/signed URL.
- [ ] Xóa tài khoản dọn cả bản xuất, hỗ trợ, ảnh và job chạy muộn; chưa dọn xong chỉ báo tiếp nhận/đang xử lý.
- [ ] Công bố chính sách lưu từng loại dữ liệu và backup; chấp thuận AI/analytics hoạt động đúng như mô tả.
- [ ] Kiểm tra log, APM, analytics và báo lỗi không nhận password, token, ảnh, ghi chú riêng hoặc nội dung form nhạy cảm.

## Hạ tầng và vận hành

- [ ] Domain/HTTPS, CORS, Auth callback/SMTP, quota và secret production được cấu hình; staging tách dữ liệu/khóa.
- [ ] Build backend có wheel Rust đúng runtime, health/readiness hợp lệ; frontend không chứa khóa đặc quyền.
- [ ] Backup DB và Storage có người phụ trách; diễn tập restore cả hai, đo thời gian/mức dữ liệu có thể mất rồi công bố mục tiêu nội bộ.
- [ ] Scheduler/worker có cảnh báo khi ngừng; thử dừng giữa chừng và tiếp tục bản xuất/xóa/dọn mà không tạo dữ liệu trùng.
- [ ] Có người trực lỗi Auth/email, lỗi 5xx, worker tồn lâu, dung lượng/egress và chi phí AI; thống nhất ngưỡng cảnh báo theo thử nghiệm.
- [ ] Có runbook thu hồi/đổi secret, tắt AI qua cấu hình, bảo trì và phản hồi sự cố; hỗ trợ có người kiểm tra phiếu.
- [ ] Rà dependency và cấu hình bảo mật trước phát hành; không có lỗ hổng nghiêm trọng đã biết chưa được xử lý hoặc quyết định khắc phục.

## Phát hành và rollback

1. Migration tương thích ngược trên staging → backup → kiểm tra quyền → build backend/frontend.
2. Smoke test tài khoản mới và tài khoản có dữ liệu, email thật, ảnh thật, xác nhận/hủy mặc và hỗ trợ.
3. Mở beta giới hạn; theo dõi lỗi, công việc tồn và chi phí trước khi mở rộng.
4. Khi lỗi: ngừng tính năng bị ảnh hưởng/rollback artifact đã xác minh; giữ API/schema tương thích. Migration phá hủy cần kế hoạch riêng, không tự chạy down migration làm mất dữ liệu.

Không tự đặt cam kết uptime, số người dùng hỗ trợ hoặc thời gian phản hồi khi chưa đo và chưa có người vận hành. Mốc ra mắt theo các điều kiện trên và [tiêu chí MVP](../san-pham/pham-vi-va-lo-trinh.md).

## Đọc tiếp

- [Kế hoạch kiểm thử](kiem-thu.md)
- [Phát hành và vận hành](phat-hanh-va-van-hanh.md)
