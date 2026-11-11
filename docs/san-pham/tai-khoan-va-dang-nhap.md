# Closet Loop — Tài khoản và đăng nhập

[Mục lục](../README.md) · Cập nhật: 11/11/2026

Phạm vi bản ra mắt: email và mật khẩu. Danh tính do Supabase Auth quản lý theo kiến trúc đề xuất; Google/Apple và MFA cho người dùng thuộc giai đoạn sau.

## Đăng ký và xác minh email

1. Nhập email, mật khẩu, nhập lại mật khẩu; đọc Điều khoản sử dụng và Chính sách quyền riêng tư qua liên kết mở được trước khi đăng nhập.
2. Tích “Tôi chấp nhận Điều khoản sử dụng và đã đọc Chính sách quyền riêng tư”, không tích sẵn. Nếu chưa xác nhận, chưa gửi yêu cầu tạo tài khoản.
3. Hiển thị **Kiểm tra email của bạn**, cho sửa email hoặc gửi lại sau thời gian chờ do dịch vụ trả về.
4. Mở liên kết xác minh → kiểm tra callback → tạo hồ sơ/cài đặt mặc định → chuyển đến hướng dẫn bắt đầu.

- Chưa xác minh email thì chưa vào tủ đồ. Không tạo tài khoản ứng dụng bằng email chưa xác nhận.
- Liên kết hết hạn/đã dùng: giải thích và cho gửi lại; nếu đã xác minh thì quay về đăng nhập.
- Thông báo đăng ký không tiết lộ một địa chỉ đã có tài khoản hay chưa.
- Đề xuất tối thiểu 12 ký tự; giới hạn tối đa theo khả năng Auth/SDK được khóa khi triển khai, hiển thị rõ và không âm thầm cắt chuỗi. Cho dán và dùng trình quản lý mật khẩu; mức tối thiểu phải được Auth thực thi, không chỉ kiểm tra trên form.

## Đăng nhập và phiên làm việc

- Email + mật khẩu, nút hiện/ẩn mật khẩu, **Quên mật khẩu**, liên kết đăng ký.
- Sai thông tin: “Email hoặc mật khẩu chưa đúng”; không chỉ rõ email có tồn tại.
- Thành công: người mới tới `/onboarding`, người cũ tới `/today` hoặc đường dẫn nội bộ hợp lệ họ đang mở.
- Hết phiên: xóa dữ liệu riêng trong bộ nhớ giao diện, chuyển tới đăng nhập; chỉ giữ đường dẫn quay lại, không đưa nội dung form riêng vào URL.
- Tự làm mới phiên khi còn hợp lệ; nếu không được, yêu cầu đăng nhập lại. Không gửi lặp vô hạn một thao tác lưu.
- Giới hạn đăng nhập/gửi lại/khôi phục do Auth áp dụng; hiện thời gian thử lại khi có, không tự đoán một con số cố định.

## Quên và đặt lại mật khẩu

Nhập email → “Nếu địa chỉ này có tài khoản, bạn sẽ nhận được hướng dẫn” → mở liên kết hợp lệ → nhập mật khẩu mới hai lần → xác nhận thành công → đăng nhập lại.

- Chỉ hiện form đặt lại sau khi xác thực phiên khôi phục; truy cập trực tiếp không đủ quyền đổi mật khẩu.
- Hết hạn/đã dùng/mở sai luồng: cho yêu cầu liên kết mới, không báo đổi thành công.
- Không yêu cầu mật khẩu cũ trong luồng khôi phục. Kiểm tra riêng hành vi này khi bật bảo vệ đổi mật khẩu tại Auth.
- Thu hồi refresh token các phiên cũ sau khôi phục; kiểm thử cả thiết bị khác, không hứa mọi access token đã phát mất hiệu lực ngay.

## Bảo mật và đăng xuất

| Thao tác | Hành vi sản phẩm |
| --- | --- |
| Đổi mật khẩu trong cài đặt | Mật khẩu hiện tại + mới + nhập lại; xử lý xác thực bổ sung nếu Auth yêu cầu |
| Đổi email | Gửi yêu cầu xác minh; vẫn hiện email hiện tại và email đang chờ, chỉ đổi sau khi Auth xác nhận |
| Đăng xuất thiết bị này | Chỉ kết thúc phiên hiện tại; xóa cache riêng của tài khoản và quay về đăng nhập |
| Đăng xuất mọi thiết bị | Có xác nhận; báo kết quả sau khi dịch vụ chấp nhận thu hồi các phiên |
| Xóa tài khoản | Nhập lại mật khẩu và xác nhận nội dung sẽ bị xóa; theo [luồng quyền riêng tư](quyen-rieng-tu.md) |

MVP có hai lựa chọn đăng xuất trên; chưa hiển thị danh sách thiết bị/vị trí nếu chưa xây cơ chế quản lý phiên tương ứng. Supabase có scope `local`/`global`; access token đã cấp có thể còn hiệu lực tới hạn. [Tài liệu đăng xuất](https://supabase.com/docs/guides/auth/signout).

## Tiêu chí nghiệm thu

- [ ] Đi hết đăng ký → xác minh → đăng nhập → đăng xuất bằng email thật trên staging.
- [ ] Có màn hình cho link sai/hết hạn, email chậm, mất mạng, giới hạn gửi và phiên hết hạn.
- [ ] Khôi phục/đổi mật khẩu, đổi email và đăng xuất mọi thiết bị được thử trên hai trình duyệt.
- [ ] Mật khẩu/token không xuất hiện trong log, analytics, URL điều hướng hoặc thông báo hỗ trợ.

## Đọc tiếp

- [Hướng dẫn bắt đầu và hồ sơ](bat-dau-va-ho-so.md)
- [Bố cục tài khoản](../thiet-ke/tai-khoan.md)
- [Tích hợp tài khoản phía backend](../backend/tai-khoan-va-cai-dat.md)
