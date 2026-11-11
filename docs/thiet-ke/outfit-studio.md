# Closet Loop — Bố cục Outfit Studio

[Mục lục](../README.md) · Cập nhật: 11/11/2026

## Outfit Studio

```text
Desktop
┌───────────────────────────────────────────────────────────────┐
│ [Quay lại]  Tên outfit...               [Lưu] [Lên lịch]     │
├──────────────────┬─────────────────────────┬──────────────────┤
│ Chọn món         │ Bàn phối 3:4            │ Món đang chọn    │
│ [Tìm/lọc]        │                         │ [Thu/phóng]      │
│ [Áo] [Quần]      │      [Áo]               │ [Lên trước]      │
│ [Váy] [Giày]     │      [Quần]             │ [Ra sau]         │
│ ...              │ [Túi]       [Giày]      │ [Bỏ khỏi outfit] │
│                  │                         │ Ghi chú/nhãn     │
└──────────────────┴─────────────────────────┴──────────────────┘
```

- Vùng chọn món khoảng 280 px; vùng thuộc tính khoảng 240 px khi đủ chỗ; bảng phối ở giữa tự co theo chiều cao/chiều rộng.
- Mobile: tên và Lưu ở trên; bàn phối ở giữa; thanh món đã chọn phía dưới; **Thêm món** mở bottom sheet. Thuộc tính xuất hiện trong sheet của món được chọn.
- Chọn bằng chạm/click để thêm; kéo chỉ để di chuyển trong bảng. Có nút dịch vị trí/đổi kích thước và hỗ trợ phím mũi tên.
- Dùng Pointer Events, pointer capture và `touch-action` chỉ trên vùng thao tác phù hợp để kéo không cuộn nhầm cả trang. Pointer Events thống nhất đầu vào chuột/chạm/bút. [MDN Pointer Events](https://developer.mozilla.org/en-US/docs/Web/API/Pointer_events).
- Lưu `x/y/w/h` theo tỉ lệ 0–1 của bảng; khóa tỉ lệ ảnh và chặn tràn khỏi bảng. Không lưu vị trí bằng pixel màn hình.
- Render preview bằng cùng mô hình DOM/CSS; MVP không cần lưu một ảnh ghép riêng để đọc lại outfit.
- Dùng phiên bản tăng dần khi sửa; nếu có thay đổi từ tab khác, báo xung đột và cho tải lại, không ghi đè âm thầm.
- Lên lịch chỉ dùng bản đã lưu; nếu đang có thay đổi, lưu thành công rồi mới mở chọn ngày.

## Đọc tiếp

- [Chức năng Studio](../san-pham/chuc-nang-mvp.md)
- [Frontend](../frontend/cau-truc.md)
