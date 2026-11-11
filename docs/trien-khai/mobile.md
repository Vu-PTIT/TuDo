# Closet Loop — Mở rộng sang mobile

[Mục lục](../README.md) · Cập nhật: 11/11/2026

## Đường mở rộng sang mobile

Khi có nhu cầu ứng dụng di động, đề xuất **React Native + Expo**, vẫn dùng Supabase Auth/Database/Storage. Expo có công cụ để phát triển Android/iOS; cần kiểm tra SDK và môi trường thiết bị tại thời điểm bắt đầu. [Hướng dẫn tạo dự án Expo](https://docs.expo.dev/get-started/create-a-project/).

- Dùng lại schema, quy tắc nghiệp vụ, hợp đồng dữ liệu và token thiết kế khi phù hợp.
- Giao diện Next.js dùng DOM không chuyển nguyên sang React Native; Studio, chọn ảnh, điều hướng và gesture cần làm UI tương ứng.
- Mobile dùng Supabase Auth và gọi cùng backend REST API `/api/v1` bằng Bearer token; upload theo quyền được backend cấp. RLS/RPC tiếp tục được backend sử dụng cho dữ liệu nghiệp vụ.
- Thêm `mobile/` cạnh `frontend/` và `backend/`. Chỉ tạo shared package khi xuất hiện phần mã cần dùng chung; ưu tiên sinh type/client từ hợp đồng OpenAPI đã có.
- Push notification, widget, đồng bộ ngoại tuyến và phát hành store là phạm vi riêng ở giai đoạn mobile. Hộp thông báo trong ứng dụng và cài đặt đã có hợp đồng Web/API để dùng lại.

## Đọc tiếp

- [Kiến trúc](../kien-truc/tong-the.md)
- [API](../api/hop-dong.md)
