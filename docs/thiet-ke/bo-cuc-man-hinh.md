# Closet Loop — Bố cục màn hình

[Mục lục](../README.md) · Cập nhật: 11/11/2026

Wireframe mô tả thứ tự và phân vùng, chưa phải bản thiết kế pixel hoàn chỉnh.

Màn hình nền tảng được tách riêng: [đăng nhập/tài khoản](tai-khoan.md), [cài đặt/hồ sơ](cai-dat-va-ho-so.md), [thông báo/hỗ trợ và lỗi toàn ứng dụng](thong-bao-va-ho-tro.md).

## Hôm nay

```text
Desktop
┌──────────────┬─────────────────────────────────────────────────┐
│ Closet Loop  │ Hôm nay, 11/11                         [Avatar] │
│              ├───────────────────────────────┬─────────────────┤
│ Hôm nay      │ Outfit cho hôm nay            │ Sắp tới         │
│ Tủ đồ        │ [Ảnh phối lớn]                │ [Ngày + outfit] │
│ Outfit       │ Đi làm                        │ [Mở lịch]       │
│ Lịch mặc     │ [Đã mặc] [Đổi outfit]         │                 │
│ Girl Math    ├───────────────────────────────┴─────────────────┤
│              │ Phối tiếp từ tủ của bạn                          │
│              │ [Một vài món]                     [Tạo outfit] │
└──────────────┴─────────────────────────────────────────────────┘
```

- Điện thoại: ngày → outfit hôm nay → nút đã mặc → các mục còn lại hôm nay → ngày sắp tới.
- Khi có nhiều outfit hôm nay, mỗi outfit có trạng thái xác nhận riêng; không có nút xác nhận chung thiếu rõ ràng.
- Chưa có lịch: “Bạn chưa chọn đồ cho hôm nay” + **Chọn outfit**. Tủ còn trống: **Thêm món đầu tiên**.

## Tủ đồ và chi tiết món

```text
┌───────────────────────────────────────────────────────────────┐
│ Tủ đồ của bạn                              [+ Thêm món]      │
│ [Tìm theo tên...]                          [Bộ lọc]          │
│ Tất cả   Áo   Quần   Váy   Giày   Túi   Phụ kiện              │
│ Đang lọc: Màu kem ×                                           │
├──────────────┬──────────────┬──────────────┬───────────────────┤
│ [Ảnh đồ]     │ [Ảnh đồ]     │ [Ảnh đồ]     │ [Placeholder]     │
│ Cardigan kem │ Jeans xanh   │ Váy hoa      │ Túi đen           │
│ Sẵn sàng     │ Đang giặt    │ Sẵn sàng     │ Chưa có ảnh       │
└──────────────┴──────────────┴──────────────┴───────────────────┘
```

- Card ảnh tỉ lệ 1:1, `object-fit: contain`, nền surface; tên tối đa hai dòng. Không đặt giá mua nổi bật trên mọi card.
- Thanh loại cuộn ngang trên điện thoại; bộ lọc mở sheet có **Áp dụng** và **Xóa bộ lọc**.
- Không có kết quả: giữ thanh tìm/lọc và nút xóa điều kiện; không hiển thị nhầm thành “tủ trống”.
- Chi tiết desktop: ảnh lớn bên trái; tên, thuộc tính, trạng thái, CPW, lịch sử và thao tác bên phải. Mobile xếp theo cùng thứ tự.
- Thao tác chính **Thêm vào outfit**; sửa ở nút phụ; xóa ở menu riêng có xác nhận.
- Menu chi tiết có **Tải ảnh**, chọn ảnh đã chuẩn hóa/bản tách nền nếu có; placeholder không có thao tác này. Tải qua API kiểm tra quyền, không công khai URL ảnh.

## Thêm/sửa món

- Hai lựa chọn ban đầu: **Thêm bằng ảnh** và **Tạo thẻ tạm**.
- Desktop: vùng ảnh bên trái, form bên phải; mobile: ảnh trước, form sau.
- Chỉ tên và loại bắt buộc ngoài nguồn ảnh/placeholder. Giá mua, size, thương hiệu nằm trong nhóm “Thông tin thêm”.
- Tách nền: xem trước ảnh ban đầu/kết quả, có nút chọn ảnh; không tự đổi ảnh khi người dùng đã lưu.
- Footer **Lưu món đồ**, disable lúc đang ghi; nếu lỗi, giữ nguyên form và hiển thị lỗi cạnh trường hoặc vùng ảnh tương ứng.

## Outfit Studio

Xem [bố cục và thao tác Studio](outfit-studio.md).

## Lịch mặc

```text
┌───────────────────────────────────────────────────────────────┐
│ Lịch mặc                [Tuần | Tháng] [Hôm nay] [<] [>]      │
├────────┬────────┬────────┬────────┬────────┬────────┬─────────┤
│ T2     │ T3     │ T4     │ T5     │ T6     │ T7     │ CN      │
│ [Bộ A] │ [+]    │ [Bộ B] │        │ [Bộ C] │        │         │
│        │        │ [Bộ D] │        │        │        │         │
├────────┴────────┴────────┴────────┴────────┴────────┴─────────┤
│ Ngày đang chọn: outfit + sự kiện + trạng thái + thao tác       │
└───────────────────────────────────────────────────────────────┘
```

- Mobile ban đầu dùng dải 7 ngày và danh sách ngày chọn; sau khi user lưu tùy chọn, mở theo `planner_default_view` tuần/tháng trên mọi thiết bị. Chế độ tháng giữ ô gọn, mở danh sách ngày để xem đủ outfit.
- Bấm ngày → xem các mục → **Thêm outfit**. Bấm mục → xem ảnh và **Đã mặc/Bỏ qua**.
- Mục đã mặc có **Hủy xác nhận**; không sửa nội dung âm thầm. Cảnh báo đồ đang giặt hiện ở mục bị ảnh hưởng.
- Nhãn ngày dùng tiếng Việt; bắt đầu tuần vào thứ Hai. Tôn trọng múi giờ hồ sơ khi xác định Hôm nay.

## Girl Math

- Phần đầu: số món đang quản lý, outfit đang lưu và lượt mặc; không làm dashboard nhiều biểu đồ trong MVP.
- Nội dung chính: danh sách món có CPW, ảnh nhỏ, giá mua, lượt mặc và liên kết mở món.
- Món chưa có giá/chưa mặc có lời giải thích đúng trạng thái, không hiển thị số 0 giả.
- Ví dụ nội dung: “Váy hoa: 30.000đ/lần mặc sau 10 ngày sử dụng”.
- Nếu lọc theo thời gian ở giai đoạn sau, phải ghi rõ CPW toàn thời gian hay theo kỳ; MVP dùng toàn thời gian.

## Bestie và Public Pass — bố cục dự kiến cho giai đoạn sau

- **Bestie:** danh sách bạn → chi tiết quyền chia sẻ với danh sách món, hạn dùng, nút thu hồi → khu vực đề xuất nhận/gửi. Studio phối hộ phải luôn ghi rõ đang phối cho ai.
- **Tủ Pass của tôi:** danh sách bài nháp/đang hiển thị/đã pass; mỗi bài có xem trước và ẩn.
- **Tủ Pass công khai:** thông tin công khai tối thiểu của chủ tủ → lưới món → chi tiết tình trạng/size → **Liên hệ Facebook** hoặc **Liên hệ Zalo** theo kênh chủ tủ cung cấp.
- Không hiển thị giá mua hoặc dữ liệu thống kê riêng trên trang public. Link liên hệ cần kiểm tra giao thức và đích đến hợp lệ; không tự tạo deep link từ dữ liệu chưa xác minh.

## Đọc tiếp

- [Điều hướng](dieu-huong.md)
- [Studio](outfit-studio.md)
