# Closet Loop — Quyền riêng tư và dữ liệu cá nhân

[Mục lục](../README.md) · Cập nhật: 11/11/2026

Đây là yêu cầu sản phẩm để triển khai và rà soát chính sách trước ra mắt, chưa phải nội dung điều khoản pháp lý đã được phê duyệt.

## Quyền riêng tư mặc định

- Hồ sơ, tủ, giá mua, outfit, lịch và lịch sử mặc chỉ chủ tài khoản được xem ở MVP.
- Thông báo rõ nhà cung cấp và mục đích trước lần gửi ảnh sang AI; có thể chọn lưu ảnh ban đầu. Không đồng ý AI vẫn dùng được tủ đồ.
- Ghi nhận phiên bản thông báo xử lý AI mà người dùng đã chấp thuận; khi nhà cung cấp/mục đích thay đổi cần hỏi lại trước lần gửi tiếp theo.
- Đo lường hành vi là tùy chọn độc lập; không gộp vào việc chấp nhận điều khoản. Tắt thì ngừng gửi sự kiện tùy chọn và xóa hàng đợi sự kiện chưa gửi.
- Không dùng ảnh riêng làm dữ liệu demo, nội dung công khai hoặc dữ liệu huấn luyện theo một giả định mặc định.

## Tải bản sao dữ liệu

1. Vào Quyền riêng tư → **Yêu cầu bản sao dữ liệu**.
2. Hiển thị `đang chờ/đang chuẩn bị/sẵn sàng/thất bại/hết hạn`; tải lại trang vẫn thấy yêu cầu gần nhất.
3. Khi sẵn sàng, tải qua endpoint kiểm tra chủ tài khoản; đề xuất file có hiệu lực 24 giờ.

- Bản ra mắt xuất **JSON dữ liệu ứng dụng**: hồ sơ, cài đặt, chấp thuận, món, outfit, lịch, lịch sử mặc, thông báo và yêu cầu hỗ trợ của chính người dùng; gồm dữ liệu lịch sử/xóa mềm còn được hệ thống lưu.
- Ghi rõ trước thao tác: bản JSON không kèm tập tin ảnh; ảnh có thể tải riêng tại chi tiết món. Không mô tả đây là bản sao đầy đủ ảnh.
- Ở chi tiết món, **Tải ảnh** tải bản ảnh gốc đã chuẩn hóa hoặc bản tách nền đã có, đúng quyền chủ; không gọi ảnh đã bỏ EXIF là tập tin upload nguyên bản.
- Không xuất mật khẩu/hash, session, secret, log nội bộ, ghi chú xử lý nội bộ hoặc signed URL.
- Có `schema_version`, thời điểm chụp dữ liệu; dùng một snapshot nhất quán, không ghép các trang dữ liệu ở thời điểm khác nhau.
- Đề xuất tối đa một yêu cầu đang chạy và một yêu cầu mới mỗi 24 giờ/tài khoản; thất bại kỹ thuật được thử lại có giới hạn.

## Xóa tài khoản

Thông tin sẽ xóa → gợi ý tải dữ liệu trước → nhập mật khẩu hiện tại + gõ **XÓA TÀI KHOẢN** → xác nhận → server tiếp nhận → kết thúc phiên.

- Nêu rõ không thể dùng tài khoản trong lúc dọn và không có luồng tự khôi phục sau khi đã tiếp nhận.
- Phản hồi đầu tiên là **Đã tiếp nhận yêu cầu**, có mã tham chiếu; không gọi đăng xuất là “đã xóa xong”.
- Dọn ảnh, bản xuất, hồ sơ/cài đặt, thông báo, yêu cầu hỗ trợ và dữ liệu nghiệp vụ; chặn dữ liệu/job mới ngay từ lúc tiếp nhận.
- Bản ghi vận hành tối thiểu chỉ giữ theo chính sách đã công bố; không giữ nội dung hỗ trợ/ảnh trong log để né luồng xóa.
- Không dùng thông báo trong app làm kênh báo hoàn tất vì tài khoản sẽ bị đóng. Khi cần kiểm tra, liên hệ kênh hỗ trợ công khai cùng mã tham chiếu; mã này không phải quyền truy cập dữ liệu.
- Bản sao đã tải về và dữ liệu trong backup có vòng đời riêng. Công bố thời hạn lưu; nếu khôi phục backup, áp dụng lại danh sách yêu cầu xóa trước khi mở dịch vụ.

## Nội dung công khai cần chuẩn bị

| Trang | Nội dung cần có trước khi nhận người dùng thật |
| --- | --- |
| `/privacy` | Loại dữ liệu, mục đích, nhà cung cấp, thời gian lưu, AI, đo lường, tải/xóa dữ liệu và đầu mối liên hệ |
| `/terms` | Chủ thể vận hành, phạm vi dịch vụ, tài khoản, quyền nội dung, hành vi không cho phép, thay đổi/ngừng dịch vụ |
| `/help` | Hướng dẫn yêu cầu hỗ trợ, mất tài khoản, dữ liệu và sự cố ảnh |

Chủ dự án phải điền thông tin vận hành thật và rà soát nội dung áp dụng tại Việt Nam trước ra mắt; không phát hành trang placeholder hoặc tuyên bố tuân thủ chưa được kiểm chứng.

## Đọc tiếp

- [Vòng đời dữ liệu](../database/vong-doi-du-lieu.md)
- [Tài khoản và bản xuất phía backend](../backend/tai-khoan-va-cai-dat.md)
