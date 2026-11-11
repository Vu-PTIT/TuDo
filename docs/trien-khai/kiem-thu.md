# Closet Loop — Kế hoạch kiểm thử

[Mục lục](../README.md) · Cập nhật: 11/11/2026

## Kiểm tra quan trọng khi triển khai

| Nhóm | Tình huống cần kiểm tra |
| --- | --- |
| Phân quyền | User B đọc/sửa món, outfit, lịch, ảnh và job của A; truy cập trực tiếp Data API/RPC; gán asset/món khác chủ |
| Tài khoản | Đăng ký/xác minh/resend, link hết hạn/đã dùng, recovery, đổi email/mật khẩu, logout local/global trên hai trình duyệt, hạn mức Auth |
| Bootstrap/hướng dẫn | User chưa xác minh bị chặn, thiếu điều khoản, callback thiết bị khác, bootstrap đồng thời, bỏ qua/tiếp tục và không reset hồ sơ cũ |
| Cài đặt | Lưu thật sau tải lại/đổi thiết bị, conflict hai tab, timezone không dịch lịch sử, mặc định Planner có tác dụng, tắt analytics ngừng sự kiện |
| Tích hợp frontend/backend | Bearer token hết hạn/sai, CORS/preflight, lỗi mạng, SSR chuyển đúng token, thay API không làm lệch kiểu dữ liệu, bundle frontend không chứa secret backend |
| Ảnh | Sai định dạng, file hỏng, quá kích thước, quá megapixel, upload dở, ảnh có EXIF, AI lỗi/timeout/hết quota |
| Studio | Kéo/chọn bằng chạm và bàn phím; không tràn bảng; đổi kích thước viewport không đổi bố cục lưu; xung đột hai tab |
| Lịch và log | Nhấn xác nhận đồng thời; hai outfit cùng ngày chung món; hủy một log; retry xác nhận cũ sau khi hủy; ngày tương lai; ranh giới múi giờ |
| Lịch sử | Sửa outfit gốc, xóa/lưu trữ món, hủy xác nhận rồi đổi lịch, xóa tài khoản khi còn job ảnh |
| CPW | Thiếu giá, giá 0, chưa mặc, làm tròn hiển thị, sửa giá mua và số ngày mặc |
| Khôi phục | Thử khôi phục cả database và object ảnh; không coi backup database là backup Storage |
| Bản xuất/xóa | JSON snapshot nhất quán đúng owner/whitelist, không kèm ảnh như UI đã nói, file hết hạn, tải ID khác chủ, retry/worker chết/lease cũ; xóa khi còn upload/job/bản xuất ghi muộn |
| Thông báo/hỗ trợ | Cùng sự kiện không trùng thông báo, tắt preference, read-all với thông báo đến sau; phiếu chống trùng/429, plain text và diagnostics không có secret; chỉ chủ xem được |
| Nội dung/vận hành | Help/chính sách mở không cần Auth; SMTP thật, phiếu tới người trực, scheduler bị dừng có cảnh báo, restore áp dụng lại sổ yêu cầu xóa |

Các kiểm tra trên là kế hoạch cho giai đoạn viết mã; chưa được thực thi trên ứng dụng.

## Python và Rust

- pytest: schema, service, phân quyền, RPC, job và adapter native.
- cargo test: ảnh lỗi/quá giới hạn, orientation, metadata, alpha và output hợp lệ.
- Integration: wheel đúng môi trường; chuyển lỗi Rust sang lỗi HTTP; xử lý native có giới hạn concurrency và không chặn event loop.
- Playwright: đăng nhập → thêm món → outfit → lên lịch → xác nhận/hủy → Girl Math.
- E2E nền tảng: đăng ký/xác minh → bỏ qua hướng dẫn → sửa settings → đăng nhập thiết bị khác → tải JSON → gửi phiếu; luồng xóa chạy trên tài khoản thử riêng.
- Kiểm tra cookie/cache/SSR khi đổi tài khoản: UI không lộ hồ sơ, thông báo hoặc tủ của user trước. Token còn hạn sau logout không được mô tả là đã bị thu hồi tức thì.

## Đọc tiếp

- [MVP](../san-pham/chuc-nang-mvp.md)
- [Build/phát hành](phat-hanh-va-van-hanh.md)
- [Điều kiện ra mắt](san-sang-ra-mat.md)
