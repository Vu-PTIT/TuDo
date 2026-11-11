# Closet Loop — Quyết định và giả định

[Mục lục](../README.md) · Cập nhật: 11/11/2026

**Đã chốt:** Web trước, mobile sau; frontend/backend tách riêng; backend dùng **Python + Rust**. Framework và cách tích hợp là đề xuất.

## Quyết định đã chốt và giả định còn lại

- **Đã chốt với chủ dự án:** ưu tiên Web responsive cho điện thoại và máy tính; phát triển ứng dụng di động ở giai đoạn sau.
- **Yêu cầu cấu trúc mã nguồn:** frontend và backend tách riêng; trong mỗi phần chia tiếp theo chức năng và trách nhiệm. Chi tiết ở [cấu trúc repository](../kien-truc/cau-truc-repository.md).
- Giao diện đầu tiên bằng tiếng Việt; tiền tệ VND; một tài khoản có một tủ đồ cá nhân.
- Chưa có yêu cầu cố định về đội ngũ, ngân sách và thời hạn; backend đã chốt Python + Rust.
- MVP kiểm chứng vòng lặp quản lý → phối → lên lịch → ghi nhận mặc; chưa triển khai thanh toán Premium.
- Một ngày có thể có nhiều outfit, ví dụ đi làm và đi chơi. Thống kê mỗi món tính tối đa một lượt mặc trong một ngày.

## Trạng thái các quyết định trước khi triển khai

| Quyết định | Phương án trong tài liệu | Trạng thái hoặc mốc cần chốt |
| --- | --- | --- |
| Nền tảng đầu tiên | Web responsive trước, mobile app sau | Chủ dự án đã xác nhận |
| Cấu trúc mã nguồn | `frontend/` và `backend/` riêng, mỗi phần có module và thư mục con rõ ràng | Chủ dự án yêu cầu |
| Ngôn ngữ backend | Python + Rust | Chủ dự án đã chốt |
| Framework backend | FastAPI; Rust tích hợp qua PyO3/maturin | Đề xuất triển khai |
| Frontend | TypeScript với Next.js | Đề xuất triển khai |
| Phạm vi ghi nhận mặc | Một lượt/món/ngày; nhiều outfit/ngày | Trước khi tạo schema và UI lịch |
| Hạn mức/nhà cung cấp AI | Chưa chốt; nhập thủ công luôn hoạt động | Trước khi bật AI cho người dùng thật |
| Danh tính hình ảnh | Hồng berry, nền sáng hơi tím, ảnh quần áo là trọng tâm | Trước khi code giao diện chi tiết |
| Kế hoạch phát hành | Theo tiêu chí hoàn tất, chưa có ngày hoặc ước lượng nhân lực | Sau khi có đội ngũ và ngân sách |
| Phạm vi vận hành thật | Auth hoàn chỉnh, hồ sơ/cài đặt, dữ liệu cá nhân, thông báo và hỗ trợ | Chủ dự án yêu cầu bổ sung; hành vi chi tiết là đề xuất trong các file chuyên đề |
| Email và người trực | SMTP riêng, domain gửi/nhận, đầu mối hỗ trợ và cảnh báo | Chủ dự án điền thông tin thật trước beta |
| Chính sách lưu dữ liệu | Bản xuất 24 giờ, thông báo 90 ngày, phiếu 90 ngày sau đóng là đề xuất | Chốt theo vận hành và rà soát chính sách trước production |

**Thứ tự bắt đầu:** chốt các giả định còn lại → dựng nền tảng và quyền riêng tư → hoàn thành Tủ đồ → Studio → Planner và lượt mặc → Girl Math → tích hợp AI cơ bản → kiểm tra MVP.

## Đọc tiếp

- [Kiến trúc](../kien-truc/tong-the.md)
- [Python API](../backend/python-api.md)
- [Rust](../backend/rust-xu-ly-anh.md)
