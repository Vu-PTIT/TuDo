# Closet Loop — Vòng đời dữ liệu và ảnh

[Mục lục](../README.md) · Cập nhật: 11/11/2026

## Lưu ảnh và cấp quyền đọc

- Bucket private đề xuất: `wardrobe-media`; prefix `{owner_id}/{asset_id}/...`.
- Chỉ lưu path trong database. Cấp signed URL thời hạn ngắn sau khi kiểm tra quyền; đề xuất 5 phút cho ảnh tủ cá nhân.
- Signed URL là quyền đọc tạm thời: ai đã có URL có thể dùng đến khi hết hạn. Không ghi URL vào analytics, log công khai hoặc snapshot lâu dài.
- Trang riêng và dữ liệu có session không dùng cache công khai; không để service worker cache phản hồi hoặc ảnh riêng trong MVP.
- Món bị xóa mềm không còn được chọn mới; log cũ giữ snapshot để tính lịch sử. Mục lịch dự kiến chứa món đó phải hiển thị cảnh báo.
- Xóa tài khoản chạy theo quy trình bền vững bên dưới; không chỉ xóa Auth user rồi để lại ảnh.
- Dọn upload bỏ dở và object mồ côi theo hạn lưu được cấu hình. Phải tính cả tham chiếu từ snapshot lịch trước khi xóa ảnh cũ; đổi ảnh món không làm mất ảnh đang dùng ở lịch sử.
- Ghi rõ chính sách giữ dữ liệu trong sản phẩm trước khi phát hành.
- Bản xuất JSON ở bucket private riêng `account-exports`, không dùng bucket public; thời hạn đề xuất 24 giờ. Hồ sơ/cài đặt/consent/thông báo/phiếu hỗ trợ theo các [schema nền tảng](tai-khoan-va-cai-dat.md), không chỉ dọn bảng tủ đồ.

**Quy trình xóa tài khoản:** sau xác nhận danh tính, ghi `account_deletion_requests` và manifest đường dẫn cần dọn trước khi thu hồi session. Trạng thái đề xuất: `requested`, `running`, `failed`, `completed`; trạng thái đang xóa chặn mutation mới qua RLS/RPC và endpoint upload/AI. Tác vụ server đọc hàng yêu cầu này để tiếp tục sau gián đoạn, không phụ thuộc session đã thu hồi.

Job ảnh kiểm tra yêu cầu xóa và sự tồn tại của hồ sơ trước khi gọi nhà cung cấp, trước và sau khi ghi output; nếu đang xóa thì hủy/loại bỏ output. Tác vụ xóa chờ job đang chạy kết thúc hoặc quá hạn, quét lại prefix Storage, xóa dữ liệu rồi mới hoàn tất xóa Auth user. Việc kiểm tra trước khi ghi riêng lẻ chưa đủ xử lý race: lần quét cuối và kiểm tra sau ghi phải ngăn ảnh xuất hiện lại. Khi dọn hoàn tất, loại bỏ `user_id` và manifest khỏi bản ghi theo chính sách lưu tối thiểu, chỉ giữ thông tin vận hành cần thiết.

Quyền upload đã cấp trước khi yêu cầu xóa cũng phải được xử lý: lưu thời điểm hết hạn thực tế của mọi quyền upload còn hiệu lực. Nếu cơ chế upload kiểm tra Storage policy ở mỗi lần ghi, policy phải từ chối tài khoản đang xóa; nếu signed upload token còn dùng được độc lập, tác vụ dọn tiếp tục quét prefix đến khi tất cả token đã hết hạn rồi mới quét cuối và báo hoàn tất. Không coi việc chặn endpoint cấp token mới là thu hồi token cũ.

Manifest xóa phải bao gồm file xuất của mọi attempt và job xuất đang chạy; chờ worker dừng/quá deadline được cưỡng chế rồi quét lại, không chỉ hủy status. Phiếu hỗ trợ/diagnostics cũng được dọn; audit chỉ giữ phần tối thiểu đã loại liên hệ định danh theo chính sách.

## Backup và yêu cầu xóa

Database và object Storage có backup riêng. Chốt thời hạn lưu, quyền truy cập và người phụ trách. Bản backup không được dùng để đọc dữ liệu người dùng thường ngày; khi phục hồi phải áp dụng lại sổ yêu cầu xóa còn trong thời hạn backup trước khi mở truy cập.

Giữ sổ xóa tối thiểu bên ngoài bản backup vừa khôi phục, chỉ có định danh kỹ thuật cần ngăn phục hồi tài khoản đã xóa và thời điểm yêu cầu; không lưu ảnh/nội dung. Hạn giữ sổ ít nhất bao phủ các bản backup còn có thể phục hồi, sau đó dọn theo chính sách được công bố. Bản ghi xử lý xóa trong DB có thể được rút gọn sau hoàn tất; không làm mất sổ đối chiếu này.

## Đọc tiếp

- [Schema](mo-hinh-du-lieu.md)
- [Quyền](../backend/xac-thuc-va-phan-quyen.md)
