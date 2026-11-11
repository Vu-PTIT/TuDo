# Closet Loop — Phát hành và vận hành

[Mục lục](../README.md) · Cập nhật: 11/11/2026

## Artifact và triển khai

- Frontend Next.js build/deploy riêng; đề xuất Vercel hoặc môi trường Node phù hợp.
- Backend Docker nhiều stage: Rust tạo wheel; Python cài dependency và wheel; runtime chạy Uvicorn.
- Python/Rust phát hành cùng backend artifact. Kiểm tra wheel đúng OS/CPU/CPython ABI của runtime.
- Cấp API URL cho frontend, cấu hình CORS ở Python, dùng HTTPS production; health/readiness không tiết lộ dữ liệu riêng.
- Migration từ `backend/supabase/migrations/`; API cần tương thích khi frontend/backend phát hành lệch thời điểm.
- OpenAPI sinh từ route/Pydantic. Thay đổi phá vỡ hợp đồng cần phiên bản API mới hoặc lộ trình chuyển tiếp.
- Kiểm tra hạn mức hosting từng ứng dụng, tài nguyên ảnh, dung lượng, egress và chi phí AI trước beta.
- Tách dữ liệu staging/production; ảnh cá nhân không dùng làm dữ liệu demo công khai.

## Vận hành dữ liệu

- Không ghi request body chứa ảnh, mật khẩu, token hoặc signed URL vào log; chỉ ghi mã đối tượng/mã lỗi cần thiết.
- Theo dõi lỗi upload/AI, thời gian phản hồi và độ trễ xác nhận mặc. Dashboard vận hành riêng chưa cần cho MVP.
- Chốt backup database và Storage riêng; thử khôi phục trước khi người dùng phụ thuộc vào tủ đồ.
- Schema/transaction, phân quyền và luồng ảnh là các điều kiện để dữ liệu an toàn, nhất quán.
- Tác vụ dọn/xóa cần trạng thái bền vững, nhận việc có khóa và xử lý lại an toàn sau gián đoạn.
- Triển khai worker xuất JSON và scheduler cùng phiên bản schema tương thích; theo dõi tuổi job/lease/lần dọn gần nhất. Backup phục hồi phải áp dụng lại sổ xóa được giữ ngoài snapshot cũ.
- Auth dùng SMTP production; kiểm tra callback, domain, giới hạn gửi và lỗi email. Người trực có hộp thư hỗ trợ, quyền công cụ riêng và hướng dẫn phản hồi sự cố.
- Trước beta hoàn tất [điều kiện ra mắt](san-sang-ra-mat.md); không đánh dấu sẵn các gate chỉ vì đã viết tài liệu.

## Đọc tiếp

- [Môi trường và build](moi-truong.md)
- [Vòng đời dữ liệu](../database/vong-doi-du-lieu.md)
- [Kế hoạch kiểm thử](kiem-thu.md)
