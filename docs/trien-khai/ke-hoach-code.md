# Closet Loop — Kế hoạch code

[Mục lục](../README.md) · Cập nhật: 11/11/2026

## Lộ trình triển khai và kiểm tra

### Bước 1 — Nền tảng

- **Frontend:** khởi tạo Next.js, token giao diện, AppShell, Auth đủ đăng ký/xác minh/khôi phục/đổi mật khẩu-email/đăng xuất, onboarding và các trang cài đặt.
- **Backend:** Python/FastAPI, Pydantic, `/api/v1`, Auth dependency, CORS, schema/RLS; module `accounts`, `settings`, bootstrap, version và consent.
- **Tích hợp:** hai ứng dụng chạy độc lập, gọi API bằng token; thử email thật trên staging và hai tài khoản, kiểm tra callback/hết phiên trước khi đưa dữ liệu riêng vào.

### Bước 2 — Một lát cắt Tủ đồ hoàn chỉnh

- **Frontend:** feature `wardrobe`, `media`; form, lưới, chi tiết và placeholder.
- **Backend:** module `wardrobe`, `media`; API, repository, kiểm tra và chuẩn hóa ảnh bằng Rust.
- **Luồng hoàn tất:** upload → chuẩn hóa → lưu món → xem/sửa/xóa với dữ liệu thật.

### Bước 3 — Studio

- **Frontend:** feature `outfits`; bảng phối, tương tác, bản nháp và preview.
- **Backend:** module `outfits`; API lưu bố cục/version và transaction liên kết món.
- **Luồng hoàn tất:** chọn món → phối → lưu → mở lại → sửa trên điện thoại thật, có xử lý món bị xóa.

### Bước 4 — Planner, lượt mặc và Girl Math

- **Frontend:** feature `planner`, `insights`, `today`; lịch, trạng thái và chỉ số.
- **Backend:** module `planner`, `insights`; snapshot, RPC xác nhận/hủy và truy vấn CPW.
- **Luồng hoàn tất:** lên lịch → mặc → xác nhận/hủy → thống kê đúng, gồm trường hợp đếm trùng và retry cũ.

### Bước 5 — AI, dữ liệu cá nhân và vận hành ra mắt

- **Frontend:** consent/xem trước AI/fallback, bản xuất JSON/xóa tài khoản, hộp thông báo, FAQ/form hỗ trợ, chính sách thật và trạng thái lỗi toàn app.
- **Backend:** `image_jobs`, `data_exports`, `notifications`, `support`; worker xuất/xóa/dọn có lease/retry, quyền tải riêng và hạn lưu.
- **Tích hợp:** rà quyền ảnh/dữ liệu nền tảng, backup/restore và job ghi muộn; người trực xử lý thử một phiếu; hoàn tất [điều kiện ra mắt](san-sang-ra-mat.md) trên staging trước mở beta.



## Checklist sẵn sàng code

- [x] Chủ dự án đã xác nhận: Web responsive trước, mobile app sau.
- [x] Chủ dự án yêu cầu tách rõ frontend/backend và chia thư mục con theo chức năng, trách nhiệm.
- [ ] Chấp nhận phạm vi MVP, quy tắc lượt mặc/ngày và snapshot lịch.
- [ ] Duyệt palette, font, điều hướng và bốn bố cục chính: Tủ đồ, Studio, Planner, Girl Math.
- [x] Chủ dự án đã chốt backend dùng Python + Rust.
- [ ] Chốt FastAPI/PyO3/maturin, phiên bản CPython/Rust và môi trường triển khai.
- [ ] Build/import thử wheel Rust, kiểm tra adapter Python–Rust.
- [ ] Chốt hợp đồng `/api/v1`, cách truyền token, CORS, môi trường và lệnh chạy độc lập cho hai ứng dụng.
- [ ] Chốt schema, transaction xác nhận mặc và policy ảnh riêng trước khi dựng dữ liệu thật.
- [ ] Chọn nhà cung cấp AI, ngân sách thử, điều kiện dùng ảnh và cách xử lý lỗi.
- [ ] Chuẩn bị dữ liệu demo có quyền sử dụng và ảnh mẫu đại diện.
- [ ] Chốt domain/SMTP, kênh hỗ trợ, người trực, thời hạn lưu/backup và nội dung chính sách; không dùng placeholder khi production.
- [ ] Chia công việc theo các bước trong [kế hoạch code](ke-hoach-code.md); mỗi bước có luồng dùng được và tiêu chí hoàn tất rõ.

**Điểm xuất phát đề xuất:** xây một luồng đăng nhập → thêm món → xem tủ hoàn chỉnh, sau đó mở rộng theo đúng thứ tự; không cần dựng cả bảy phân hệ cùng lúc.

## Đọc tiếp

- [Môi trường](moi-truong.md)
- [Kiểm thử](kiem-thu.md)
- [Email/worker](email-va-tac-vu-nen.md)
