# Closet Loop — Transaction và ràng buộc

[Mục lục](../README.md) · Cập nhật: 11/11/2026

## Ràng buộc cần có trong migration

- Tên món/outfit: 1–100 ký tự sau trim; ghi chú tối đa 1.000 ký tự; giá mua `NULL` hoặc >= 0. Đây là giới hạn đề xuất cho ứng dụng.
- `CHECK`: `w > 0`, `h > 0`, `x >= 0`, `y >= 0`, `x + w <= 1`, `y + h <= 1`; `z_index` là số nguyên không âm.
- Mọi món trong một outfit, planner snapshot và wear log phải thuộc cùng chủ tủ. Dùng composite FK có `owner_id` hoặc function kiểm tra trong transaction, không chỉ kiểm tra ở UI.
- `asset_id` chỉ được tham chiếu ảnh `ready` cùng chủ. User không được tự gán `ready`, sửa đường dẫn xử lý hoặc trạng thái job do server quản lý.
- Giới hạn 1–12 món/outfit và kiểm tra món chưa xóa/lưu trữ ở hàm lưu; không tạo outfit trống.
- Index tối thiểu: `wardrobe_items(owner_id, category)`, `outfits(owner_id, updated_at)`, `planner_entries(owner_id, scheduled_date)`, `wear_logs(owner_id, worn_date)`, `wear_log_items(item_id, wear_log_id)`.
- Các bảng con cần FK/index tương ứng. Mọi UNIQUE và mutation có quyền đúng kể cả khi gọi trực tiếp Data API.
- Tách trạng thái đã mặc khỏi quyền cập nhật thông thường: chỉ function xác nhận/hủy xác nhận được tạo/xóa wear log và đổi trạng thái mục lịch sang/từ `worn`.

**Đường ghi database:** bảng nghiệp vụ chỉ cho `authenticated` đọc theo RLS; thu hồi quyền INSERT/UPDATE/DELETE trực tiếp và cấp quyền gọi các RPC nghiệp vụ cụ thể. Repository của backend dùng JWT người gọi để gọi các RPC này. Hồ sơ chỉ cho cập nhật tên/múi giờ qua hàm hoặc whitelist cột. Upload staging chỉ được INSERT đúng prefix đã cấp; không được ghi đè/xóa ảnh đã chuẩn hóa bằng Storage API của client.

Riêng bước hoàn tất ảnh, kết quả AI và xóa tài khoản dùng tác vụ server có quyền đặc biệt trong module hẹp, kiểm tra lại chủ sở hữu và trạng thái tài khoản. Không mở RPC nhận trạng thái `ready`/`succeeded` hoặc đường dẫn output tùy ý cho người dùng; không dùng service role cho CRUD thông thường.

## Transaction xác nhận đã mặc

1. Nhận `entry_id`, `operation_key` và `expected_version`; xác thực người gọi, khóa mục lịch và kiểm tra chủ sở hữu.
2. Nếu operation key là thao tác cuối đã lưu, trả kết quả hiện tại. Nếu là thao tác khác và version không khớp, trả `CONFLICT`; client tải trạng thái mới, không tự gửi lại ý định cũ.
3. Kiểm tra ngày không nằm trong tương lai theo múi giờ hồ sơ; ngày mặc lấy từ mục lịch, không nhận riêng từ client.
4. Nếu đã có wear log và yêu cầu vẫn hợp lệ: trả trạng thái đã mặc, không chèn thêm. Nếu chưa có, kiểm tra quyền/trạng thái các món trong snapshot.
5. Chèn `wear_logs` và `wear_log_items` từ snapshot, đổi mục lịch sang `worn`, tăng version và lưu operation key trong cùng transaction.
6. Hủy xác nhận dùng cùng cơ chế version/key: xóa log và các dòng con của mục đó, đổi lại `planned`, tăng version. Các thao tác sửa/bỏ qua mục lịch cũng tăng version.

Dùng PostgreSQL function/RPC với kiểm tra `auth.uid()`. Nếu cần `SECURITY DEFINER`, phải cố định `search_path`, giới hạn quyền EXECUTE và kiểm tra chủ sở hữu bên trong; không để function trở thành đường bỏ qua RLS.

Tính lượt mặc một món bằng `COUNT(DISTINCT worn_date)` trên log của món đó. Không lưu bộ đếm tăng/giảm thủ công trong MVP. Hai mục cùng ngày dùng một món vẫn chỉ một lượt; hủy một mục vẫn giữ lượt nếu mục còn lại đã xác nhận.

Tổng lượt mặc toàn tủ đếm các cặp `(item_id, worn_date)` khác nhau. Ví dụ yêu cầu xác nhận cũ bị mất phản hồi, sau đó người dùng hủy: retry xác nhận với version cũ phải bị từ chối, không tạo lại log.

Sửa outfit gốc không sửa snapshot lịch hoặc log cũ. Muốn sửa/xóa mục đã mặc phải hủy xác nhận trước. Sửa giá mua tính lại CPW theo giá hiện tại.

## Đọc tiếp

- [Chức năng MVP](../san-pham/chuc-nang-mvp.md)
- [Schema](mo-hinh-du-lieu.md)
