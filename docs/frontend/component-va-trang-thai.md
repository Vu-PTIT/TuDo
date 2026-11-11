# Closet Loop — Component và trạng thái UI

[Mục lục](../README.md) · Cập nhật: 11/11/2026

## Component và trạng thái dùng chung

| Component | Trách nhiệm |
| --- | --- |
| `AppShell` | Sidebar/header/bottom navigation và safe-area |
| `GarmentCard` / `GarmentImage` | Ảnh thật hoặc placeholder; tên và trạng thái |
| `WardrobeFilters` | Tìm/lọc nhất quán giữa Tủ và Studio |
| `ItemForm` / `ImageUploadField` | Form thêm/sửa, tiến trình và lỗi ảnh |
| `OutfitPreview` | Dựng bố cục từ dữ liệu đã lưu; chỉ đọc |
| `OutfitEditor` | Chọn món, di chuyển, resize, lớp và bản nháp |
| `PlannerEntryCard` | Ngày/sự kiện, preview và xác nhận mặc |
| `CostPerWearValue` | Giá trị hoặc lời giải thích thiếu dữ liệu |
| `EmptyState` / `ErrorState` | Nêu tình trạng và hành động tiếp theo |
| `ConfirmDialog` | Xóa, bỏ bản nháp, hủy xác nhận, xóa tài khoản |
| `AuthForm` / `PasswordField` | Form Auth, hiện/ẩn mật khẩu, lỗi theo trường; không lưu password lâu dài |
| `SettingsSection` / `SettingsForm` | Nhóm cài đặt, trạng thái lưu và cảnh báo đổi chưa lưu |
| `NotificationBell` / `NotificationList` | Số chưa đọc, danh sách và hành động đã đọc |
| `DataExportStatus` | Trạng thái yêu cầu JSON, hạn dùng và tải riêng tư |
| `SupportRequestForm` / `SupportRequestStatus` | Gửi chống lặp và trạng thái phiếu |

Mỗi màn hình dữ liệu phải xử lý đủ: đang tải, trống lần đầu, không có kết quả lọc, có dữ liệu và lỗi/thử lại. Ảnh lỗi có fallback giữ kích thước; không làm nhảy bố cục.

Dialog/sheet quản lý focus và trả focus về nút mở. Form có label, lỗi đọc được bằng screen reader; thông báo lưu/xác nhận không chỉ dựa vào màu. Kiểm tra cả bàn phím và cảm ứng.

Các component đặc thù ở feature tương ứng; chỉ đưa vào shared khi đã dùng chung. Trạng thái toàn ứng dụng gồm hết phiên, mất mạng, quota, version conflict, 404 và bảo trì theo [bố cục thông báo/hỗ trợ](../thiet-ke/thong-bao-va-ho-tro.md).

## Đọc tiếp

- [Frontend](cau-truc.md)
- [Hệ thống thiết kế](../thiet-ke/he-thong-thiet-ke.md)
