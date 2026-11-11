# Closet Loop — Chức năng MVP

[Mục lục](../README.md) · Cập nhật: 11/11/2026

## Yêu cầu chức năng MVP

### M01. Tài khoản và hồ sơ

- Đăng ký, xác minh email, đăng nhập, đăng xuất và khôi phục mật khẩu.
- Có đổi email/mật khẩu, đăng xuất mọi thiết bị; xem [đặc tả tài khoản](tai-khoan-va-dang-nhap.md).
- Hồ sơ gồm tên hiển thị và múi giờ; hướng dẫn bắt đầu bỏ qua được. [Chi tiết hồ sơ](bat-dau-va-ho-so.md).
- Tài khoản này không đọc được dữ liệu của tài khoản khác bằng cách sửa đường dẫn hay mã đối tượng.
- Có thao tác yêu cầu xóa tài khoản, xác nhận lại danh tính và xóa dữ liệu/ảnh liên quan.
- Nếu việc dọn dữ liệu cần nhiều bước, hiển thị đang xử lý; chỉ báo hoàn tất sau khi dọn xong các dữ liệu và quyền upload còn hiệu lực.

**Hoàn tất khi:** người mới tạo tài khoản và thêm được món đầu tiên; đăng xuất xóa dữ liệu riêng khỏi UI, request không có phiên hợp lệ bị chặn. JWT đã phát có giới hạn thu hồi như [đặc tả tài khoản](tai-khoan-va-dang-nhap.md).

**Nền tảng đi cùng khi ra mắt:** [cài đặt](cai-dat.md), [thông báo](thong-bao.md), [tải/xóa dữ liệu](quyen-rieng-tu.md), [hỗ trợ](ho-tro.md). Không coi việc hoàn tất các màn hình tủ đồ là đủ điều kiện phát hành.

### M02. Tủ đồ

**Thông tin một món:**

| Trường | Bắt buộc | Ghi chú |
| --- | --- | --- |
| Tên | Có | Ví dụ: Cardigan kem |
| Loại | Có | Áo, quần, váy liền, chân váy, áo khoác, giày, túi, phụ kiện, khác |
| Ảnh hoặc placeholder | Có một trong hai | Có thể thay ảnh thật sau |
| Màu | Không | Một hoặc nhiều nhãn màu |
| Size, thương hiệu, ghi chú | Không | Văn bản ngắn |
| Giá mua, ngày mua | Không | Giá mua có thể để trống, không tự điền 0 |
| Trạng thái | Có, có mặc định | Sẵn sàng, đang giặt, chưa sẵn sàng, lưu trữ |

- Hiển thị dạng lưới ảnh; tìm theo tên, lọc theo loại/màu/trạng thái.
- Trang chi tiết cho sửa thuộc tính, thay ảnh, xem lịch sử và Cost-Per-Wear.
- Món đang giặt/chưa sẵn sàng vẫn xem được; có nhãn cảnh báo khi phối hoặc lên lịch.
- Món lưu trữ được ẩn khỏi lựa chọn mặc định; người dùng có thể mở bộ lọc để tìm lại.
- Xóa món khỏi tủ dùng xóa mềm trong MVP; lịch sử đã mặc vẫn giữ thông tin snapshot. Giao diện phải giải thích điều này trước khi xóa. Xóa tài khoản là luồng xóa toàn bộ dữ liệu.

**Hoàn tất khi:** thêm/sửa/xóa một món phản ánh đúng sau tải lại; tìm và lọc kết hợp được; placeholder không bị lỗi khi mở chi tiết.

### M03. Nhập nhanh và AI cơ bản

- Ảnh đầu vào MVP: JPG, PNG hoặc WebP; giới hạn đề xuất 10 MB/ảnh và 25 megapixel sau giải mã.
- Chưa nhận HEIC trong MVP; hiển thị hướng dẫn chuyển sang JPG/PNG khi gặp định dạng này.
- Mỗi lượt nhập tạo một món; người dùng chụp món trên nền đơn giản để có kết quả tách nền tốt hơn.
- Luôn xem trước ảnh và xác nhận trước khi lưu. Tách nền không tự tạo thêm món.
- Placeholder chỉ cần tên và loại; biểu tượng theo loại và màu do người dùng chọn. Chưa cần gọi AI để đọc câu mô tả.
- Hiển thị tiến trình xử lý và hành động thử lại/giữ ảnh ban đầu khi thất bại; không mất thông tin đã nhập.
- Trước lần gửi ảnh sang dịch vụ AI bên ngoài, giải thích mục đích xử lý và cho người dùng chọn tiếp tục.

**Hoàn tất khi:** thêm đồ được cả khi AI hoạt động, khi AI lỗi và khi không có ảnh.

### M04. Outfit Studio

- Chọn món từ tủ để đưa vào bảng phối tỉ lệ 3:4.
- Kéo bằng chuột/chạm; đổi kích thước giữ tỉ lệ ảnh, đổi lớp và bỏ món khỏi bảng.
- Có cách chọn món và chỉnh vị trí bằng nút/bàn phím; thao tác kéo không phải cách duy nhất.
- Lưu tên, ghi chú, nhãn phong cách/hoàn cảnh và vị trí từng món.
- Đề xuất giới hạn MVP: 1–12 món/outfit; không bắt buộc đủ áo, quần, giày.
- Mở lại giữ đúng bố cục tương đối trên các kích thước màn hình.
- Món bị xóa/lưu trữ sau đó được đánh dấu thiếu/không sẵn sàng, không làm trang outfit bị lỗi.
- Nhắc lưu hoặc xác nhận bỏ thay đổi khi rời Studio có bản nháp chưa lưu.

**Hoàn tất khi:** lưu và mở lại outfit trên điện thoại/máy tính vẫn giữ vị trí; có thể thêm outfit vào Planner.

### M05. Outfit Planner và ghi nhận mặc

- Xem tuần/tháng, chọn ngày, thêm outfit đã lưu và tên sự kiện tùy chọn.
- Một ngày có nhiều mục; mặc định không gắn giờ cụ thể trong MVP.
- Trạng thái mục lịch: dự kiến, đã mặc, bỏ qua.
- **Đã mặc** chỉ dùng cho hôm nay hoặc ngày trước đó theo múi giờ tài khoản.
- Khi lên lịch, lưu bản chụp outfit tại thời điểm đó. Sửa outfit gốc không tự thay đổi lịch đã tạo; người dùng phải chủ động thay outfit ở mục lịch còn dự kiến.
- Xác nhận đã mặc tạo lịch sử cho đúng các món trong bản chụp của mục lịch.
- Món đang giặt/chưa sẵn sàng: cảnh báo và yêu cầu cập nhật trạng thái trước khi xác nhận. Món đã xóa/lưu trữ/đã pass phải thay hoặc bỏ khỏi mục lịch dự kiến.
- Có thể hủy xác nhận; hệ thống bỏ đóng góp của mục lịch này khỏi thống kê. Muốn sửa/xóa mục đã mặc phải hủy xác nhận trước.
- Nhấn **Đã mặc** nhiều lần hoặc tải lại không tạo thêm lượt.
- Yêu cầu gửi lại từ một thao tác cũ không được đảo ngược thao tác mới hơn, ví dụ tự xác nhận lại sau khi người dùng vừa hủy xác nhận.

**Hoàn tất khi:** xác nhận và hủy xác nhận làm thống kê thay đổi đúng, không đếm trùng hay lệch ngày.

### M06. Girl Math cơ bản

```text
Lượt mặc của một món = số ngày khác nhau có xác nhận đã mặc món đó
Cost-Per-Wear = giá mua / lượt mặc
```

- Hai outfit cùng ngày có chung một món: món đó tăng một lượt. Trên giao diện giải thích “Lượt mặc được tính theo ngày”.
- Chưa có lượt mặc: hiển thị **Chưa mặc**, không chia cho 0.
- Chưa nhập giá mua: hiển thị **Thêm giá mua để xem**, không coi là đồ miễn phí.
- Giá mua bằng 0 do người dùng chủ động nhập: Cost-Per-Wear bằng 0 khi đã có lượt mặc.
- Tính từ giá mua hiện tại; sửa lại giá mua sẽ tính lại chỉ số. Làm tròn khi hiển thị, không làm tròn dữ liệu gốc.
- Ví dụ: váy 300.000đ, mặc trong 10 ngày khác nhau → 30.000đ/lần mặc.
- Số món đang quản lý không gồm món đã xóa/lưu trữ/đã pass; số outfit đang lưu không gồm outfit đã xóa.
- Tổng lượt mặc là tổng số cặp (món, ngày) đã xác nhận, không phải số lần bấm **Đã mặc**. Lịch sử cũ vẫn đóng góp khi món được lưu trữ hoặc xóa mềm.
- Chưa hiển thị “chi phí trung bình toàn tủ” cho đến khi chốt cách xử lý món thiếu giá và cách tính trọng số.
- Chỉ số phản ánh mức sử dụng; không diễn giải là khoản tiền thu hồi hay tiết kiệm thực tế.

**Hoàn tất khi:** các trường hợp chưa mặc, thiếu giá, giá 0, hai outfit cùng ngày và hủy một trong hai đều ra kết quả đúng.

## Đọc tiếp

- [Hành trình](hanh-trinh.md)
- [Transaction](../database/transaction.md)
