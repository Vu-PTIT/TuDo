# Closet Loop — Backend tài khoản và cài đặt

[Mục lục](../README.md) · Cập nhật: 11/11/2026

Python quản lý hồ sơ, cài đặt, chấp thuận và quy trình dữ liệu. Supabase Auth là nguồn danh tính/email/mật khẩu; Rust tiếp tục chỉ xử lý ảnh.

## Khởi tạo và cập nhật tài khoản

- `accounts.bootstrap`: sau khi xác thực user và email đã xác minh, tạo `profiles` + `user_settings` + ghi nhận điều khoản trong một RPC transaction.
- Dùng khóa Auth user làm định danh, không dùng email. Retry bootstrap không tạo tủ/hồ sơ lần hai hoặc reset cài đặt đã sửa.
- Backend kiểm tra phiên bản điều khoản hiện hành; nếu thiếu chấp nhận, trả yêu cầu hiển thị form trước khi khởi tạo. Metadata Auth không quyết định quyền hay thay thế bằng chứng chấp nhận ở server.
- Không bootstrap lại tài khoản đang xóa; RPC kiểm tra yêu cầu xóa dưới khóa để tránh race với tác vụ dọn.
- PATCH hồ sơ chỉ nhận tên/múi giờ + version; PATCH cài đặt chỉ nhận các trường cho phép + version. Không nhận email, role, owner hay timestamp từ client.
- Validate mã múi giờ, độ dài tên và enum; tăng version trong transaction hoặc trả `409 CONFLICT`.
- Hướng dẫn hoàn thành/bỏ qua dùng thao tác riêng, timestamp do server sinh; cùng trạng thái gửi lại là idempotent.

## Auth và thao tác nhạy cảm

| Thao tác | Nơi xử lý |
| --- | --- |
| Đăng ký/đăng nhập/resend/recovery | Frontend gọi Supabase Auth với callback cho phép |
| Đổi email | Auth `updateUser`; giữ Secure Email Change, chỉ hiển thị thành công sau xác minh |
| Đổi mật khẩu | Auth `updateUser`, bật yêu cầu mật khẩu hiện tại và luồng xác thực bổ sung; kiểm tra recovery không yêu cầu mật khẩu bị quên |
| Đăng xuất | Gọi Auth với scope rõ `local` hoặc `global`, xóa cookie/cache frontend theo kết quả |
| Xóa dữ liệu/tài khoản | Python kiểm tra lại danh tính rồi ghi yêu cầu bền vững; worker dọn bằng quyền server giới hạn |

`updateUser` hỗ trợ đổi email/mật khẩu; tùy chọn kiểm tra mật khẩu hiện tại và nonce phụ thuộc SDK/cấu hình được chọn. Khóa phiên bản SDK tương thích và thử từng luồng trên staging. [Cập nhật user](https://supabase.com/docs/reference/javascript/auth-updateuser), [bảo vệ mật khẩu](https://supabase.com/docs/guides/auth/password-security).

Với xóa tài khoản email/mật khẩu: nhận `current_password` qua HTTPS, dùng client Auth tạm độc lập để đăng nhập lại bằng email canonical lấy từ user đã xác thực, đối chiếu đúng user ID. Không dùng client đang gắn session người khác; thu hồi riêng phiên tạm vừa tạo, không trả token về UI. Giới hạn số lần thử theo user/IP; không ghi body/mật khẩu vào log, trace hoặc công cụ báo lỗi. Mật khẩu chỉ tồn tại trong thời gian xử lý request.

Chỉ sau xác minh thành công mới tạo yêu cầu xóa dưới khóa tài khoản; kiểm tra lại trạng thái để tránh hai request chạy đua. Yêu cầu đã tiếp nhận được trả lại theo request key; không bắt đầu một quy trình xóa thứ hai.

## Chấp thuận và đo lường

- `accounts` ghi sự kiện chấp nhận điều khoản/đọc chính sách; `settings` cập nhật đo lường và ghi thay đổi chấp thuận trong cùng transaction.
- AI chỉ chạy khi có chấp thuận đúng phiên bản nhà cung cấp/mục đích hiện hành. Backend tự kiểm tra, không chỉ tin nút đồng ý ở frontend.
- Chấp thuận không cấp quyền đọc dữ liệu người khác. Client không được sửa/xóa lịch sử sự kiện đã ghi.
- Thay đổi chấp thuận có request key và expected revision theo loại; retry cũ sau lần thu hồi mới hơn không được tự bật AI lại. Điều khoản/privacy phiên bản mới có thể được ghi nhận qua endpoint consent theo loại/action được phép.
- Frontend tải cài đặt trước khi bật analytics tùy chọn; khi chưa biết trạng thái thì không gửi sự kiện.

## Bản sao dữ liệu

- Module `data_exports`: tạo yêu cầu có request key, giới hạn một yêu cầu đang chạy/tài khoản; worker nhận việc bằng lease.
- Worker dùng transaction `READ ONLY, REPEATABLE READ`, chỉ chọn bảng/trường nằm trong danh sách xuất và đúng chủ; ghi `schema_version`, `snapshot_at`. Nhiều SELECT ở mức Read Committed mặc định chưa bảo đảm cùng snapshot. [PostgreSQL transaction isolation](https://www.postgresql.org/docs/current/transaction-iso.html).
- JSON không chứa bytes ảnh, object path riêng, signed URL, token hoặc dữ liệu nội bộ; metadata ảnh gồm asset ID, tên/loại và kích thước cần thiết.
- Lưu file ở bucket private `account-exports`, prefix theo user/request; worker là bên duy nhất ghi. Ghi object trước rồi commit trạng thái `ready`; retry dọn object thừa bằng path xác định.
- Endpoint tải kiểm tra user, trạng thái tài khoản, quyền sở hữu và hạn dùng; Python stream file, `Cache-Control: private, no-store`, `Content-Disposition: attachment`. Không trả URL download công khai hoặc URL dài hạn.
- Khi xóa tài khoản: hủy yêu cầu xuất chờ, chờ/thu hồi lease đang chạy, kiểm tra tombstone trước/sau ghi, dọn cả output ghi muộn rồi mới kết thúc xóa.

## Đọc tiếp

- [API tài khoản và cài đặt](../api/tai-khoan-va-cai-dat.md)
- [Schema tài khoản](../database/tai-khoan-va-cai-dat.md)
- [Worker và email](../trien-khai/email-va-tac-vu-nen.md)
