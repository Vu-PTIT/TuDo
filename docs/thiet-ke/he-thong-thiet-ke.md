# Closet Loop — Hệ thống thiết kế

[Mục lục](../README.md) · Cập nhật: 11/11/2026

## Hệ thống thiết kế

### Hướng hình ảnh

**Ý tưởng:** một tủ đồ cá nhân và bàn phối outfit. Ảnh quần áo tách nền là nội dung chủ đạo; màu berry tạo điểm nhấn, nền sáng hơi tím giữ không gian nhẹ và rõ.

- Dùng lưới cho món đồ, bàn phối cho Studio, lịch cho Planner; mỗi chức năng có cấu trúc phù hợp.
- Giao diện ứng dụng đi thẳng vào đồ và outfit; Hôm nay không có banner quảng cáo lớn.
- Trang trí tiết chế. Cảm giác vui đến từ outfit, nhãn ngắn và phản hồi sau thao tác.
- Không giảm độ rõ của ảnh để tạo hiệu ứng “bụi” ở MVP; tính năng 90 ngày về sau có nhãn rõ ràng và tôn trọng giảm chuyển động.

### Token màu

| Token | Giá trị đề xuất | Vai trò |
| --- | --- | --- |
| `background` | `#F7F6FA` | Nền ứng dụng |
| `surface` | `#FFFFFF` | Form, vùng ảnh và mặt phẳng nội dung |
| `text-primary` | `#302734` | Chữ chính |
| `text-secondary` | `#6F6675` | Chữ phụ có ý nghĩa |
| `brand` | `#963252` | Nút chính, mục đang chọn, focus |
| `border` | `#E5DFE8` | Đường chia nội dung, viền vùng ảnh |

Màu trạng thái bổ sung: thành công `#256047`, cảnh báo `#795000`, lỗi `#B42318`; luôn có chữ hoặc biểu tượng đi kèm. Border trang trí không thay thế focus ring có độ tương phản rõ.

### Typography, kích thước và tương tác

- Font đề xuất: **Be Vietnam Pro** cho tiêu đề và nội dung; dùng các trọng lượng 400/500/600/700, kiểm tra dấu tiếng Việt khi tích hợp. [Nguồn font Google Fonts](https://github.com/google/fonts/tree/main/ofl/bevietnampro).
- Cỡ chữ: 12 px cho metadata không quan trọng, 14 px nhãn phụ, 16 px nội dung/form, 20 px tiêu đề vùng, 24–32 px tiêu đề trang.
- Line-height nội dung khoảng 1.5; văn bản dài giới hạn khoảng 65–75 ký tự/dòng; căn trái.
- Spacing dùng thang 4/8/12/16/24/32/48 px.
- Bo góc đề xuất: 10 px input/nút, 14 px vùng ảnh, 20 px dialog/sheet. Không bọc mọi dòng nội dung vào card.
- Vùng bấm tối thiểu 44×44 px; input trên điện thoại dùng chữ 16 px.
- Chuyển trạng thái khoảng 120–180 ms; hỗ trợ `prefers-reduced-motion`; không chạy hiệu ứng liên tục.
- Tương phản mục tiêu: chữ thường tối thiểu 4.5:1; kiểm tra lại khi đổi màu, giảm opacity hoặc đặt chữ lên ảnh.

## Đọc tiếp

- [Component](../frontend/component-va-trang-thai.md)
- [Điều hướng](dieu-huong.md)
