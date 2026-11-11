# Closet Loop — Upload ảnh và AI

[Mục lục](../README.md) · Cập nhật: 11/11/2026

Trước khi gọi nhà cung cấp, backend kiểm tra tài khoản hoạt động và chấp thuận AI đúng phiên bản; UI giải thích nhà cung cấp/mục đích trước lần gửi đầu tiên. Thu hồi chấp thuận chặn lần gửi mới, không thể thu hồi một yêu cầu đã gửi ra ngoài; công bố cách nhà cung cấp giữ/xóa dữ liệu theo thỏa thuận thực tế.

## Upload ảnh và tách nền

### Luồng xử lý

1. Client kiểm tra định dạng/kích thước để phản hồi sớm; gửi yêu cầu tạo upload.
2. Server xác thực, cấp `asset_id`, object path staging và quyền upload chỉ vào path đó.
3. Client upload trực tiếp vào Storage private; gọi endpoint hoàn tất.
4. Server kiểm tra chủ sở hữu, kích thước byte, loại file từ nội dung và khả năng giải mã; từ chối ảnh vượt 25 megapixel. Không chỉ tin extension/MIME client gửi.
5. Thư viện Rust `image_core` chuẩn hóa hướng ảnh, loại EXIF/metadata, tạo ảnh sạch và thumbnail; Python xóa object staging sau xử lý. `original_path` chỉ bản ảnh đã làm sạch, không phải file raw còn metadata.
6. Đánh dấu asset `ready`; cho phép lưu món thủ công ngay khi người dùng xác nhận.
7. Nếu chọn tách nền, tạo `image_jobs`, gọi nhà cung cấp từ server bằng bytes của asset hợp lệ; không nhận URL tùy ý để server tải về.
8. Kiểm tra output, lưu cutout và trạng thái; người dùng chọn ảnh xử lý hoặc ảnh ban đầu. Chỉ đổi ảnh món sau khi người dùng xác nhận.

### Cách triển khai AI trong MVP

- Bắt đầu bằng một lời gọi server có timeout giới hạn, ví dụ 20 giây sau khi xác minh hạn mức của nơi host. UI hiển thị đang xử lý và có fallback ảnh ban đầu.
- Endpoint chờ kết quả trong request; không trả “đã xếp hàng” rồi trông chờ tác vụ trong bộ nhớ tiếp tục sau khi request kết thúc.
- Nếu request bị ngắt, job quá hạn phải được nhận diện là lỗi/không rõ kết quả khi đọc lại. Không giữ spinner vô hạn và không tự động gọi lại nhà cung cấp có tính phí.
- `request_key` chống việc nhấn lặp tạo nhiều job nội bộ; không bảo đảm nhà cung cấp chỉ tính phí một lần khi timeout. Chỉ bật retry tự động nếu nhà cung cấp có cơ chế idempotency tương ứng.
- Giới hạn số job đồng thời và số lượt theo tài khoản/ngày; cấu hình theo ngân sách thử nghiệm. Hết hạn mức vẫn cho lưu ảnh thủ công.
- Nếu xử lý thực tế thường vượt timeout, chuyển sang queue bền vững + worker rồi mới trả `202`; đó là thay đổi kiến trúc dựa trên số đo, chưa cần dựng trong bản đầu.
- Ghi mã lỗi kỹ thuật ở server và thông báo dễ hiểu trên UI; không trả khóa API hay toàn bộ phản hồi nhạy cảm của nhà cung cấp.

### Chọn nhà cung cấp

Đề xuất thử **Photoroom Background Removal API** làm ứng viên đầu tiên; chưa chốt dịch vụ hoặc ngân sách. Photoroom công bố API tách nền và chỉnh sửa ảnh sản phẩm. Đây không phải bảo đảm chất lượng cho ảnh tủ đồ thực tế. [Thông tin API của Photoroom](https://www.photoroom.com/api).

Trước khi bật cho người dùng thật, kiểm tra trên tập ảnh đại diện: đồ màu sáng/tối, chất liệu mỏng, họa tiết, phụ kiện nhỏ và nền nhiều chi tiết. Ghi tỉ lệ dùng được, thời gian xử lý, chi phí và chính sách lưu ảnh.

Nếu cân nhắc remove.bg, cần kiểm tra lại kế hoạch tích hợp: tài liệu tại ngày 11/11/2026 thông báo chuyển background removal sang Leonardo.Ai từ 01/12/2026. Không khóa dự án vào endpoint cũ. [Thông báo trên tài liệu remove.bg](https://www.remove.bg/api).

Python điều phối job, gọi nhà cung cấp và ghi dữ liệu; phần chuẩn hóa bytes ảnh dùng [thư viện Rust](rust-xu-ly-anh.md).

## Đọc tiếp

- [Quyền ảnh](xac-thuc-va-phan-quyen.md)
- [Vòng đời dữ liệu](../database/vong-doi-du-lieu.md)
