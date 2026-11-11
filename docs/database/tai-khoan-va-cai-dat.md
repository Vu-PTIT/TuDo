# Closet Loop — Dữ liệu tài khoản và cài đặt

[Mục lục](../README.md) · Cập nhật: 11/11/2026

Phần này mở rộng [schema cốt lõi](mo-hinh-du-lieu.md). Bảng danh tính/mật khẩu/session thuộc Auth; không sao chép password hash sang schema ứng dụng.

## Bảng và trường

| Bảng | Trường chính | Ràng buộc |
| --- | --- | --- |
| `profiles` — mở rộng | `id`, `display_name`, `timezone`, `onboarding_completed_at`, `onboarding_skipped_at`, `version`, timestamps | Một user/một hồ sơ; version từ 1; hai mốc hướng dẫn không đồng thời có giá trị |
| `user_settings` | `owner_id`, `planner_default_view`, `activity_notifications`, `analytics_opt_in`, `version`, timestamps | PK owner; view `week`/`month`; mặc định `week`, true, false |
| `account_consents` | `id`, `owner_id`, `kind`, `policy_version`, `action`, `revision`, `request_key`, `created_at` | Sự kiện bất biến; UNIQUE(owner_id, kind, revision) và UNIQUE(owner_id, request_key); action hợp lệ theo loại terms/privacy/ai/analytics |
| `data_export_requests` | `id`, `owner_id`, `request_key`, `status`, `snapshot_at`, `object_path`, `expires_at`, `error_code`, `attempts`, `available_at`, `lease_token`, `lease_until`, timestamps | UNIQUE(owner_id, request_key); một yêu cầu queued/running mỗi owner bằng partial unique index |
| `account_deletion_requests` — mở rộng | `request_key`, `reference_code` và trường nhận việc/lease | Một yêu cầu chưa hoàn tất/user; server-only; giữ manifest trước khi xóa bất kỳ bảng phụ thuộc nào |

`data_export_requests.status`: `queued`, `running`, `ready`, `failed`, `expired`, `cancelled`. Chỉ `ready` có file để tải và phải còn hạn; lỗi không trả chi tiết nội bộ cho user.

`account_consents.policy_version` tham chiếu phiên bản nội dung do server phát hành; bản AI bao gồm nhà cung cấp/mục đích trong phiên bản. Chính sách cấu hình không nhận giá trị tùy ý từ client. Không cần lưu IP đầy đủ chỉ để có một bản ghi chấp thuận.

## Transaction và quyền

- Bootstrap tạo profile/settings và ghi chấp thuận trong một transaction; đồng thời kiểm tra user đã xác minh, phiên bản điều khoản và không có yêu cầu xóa.
- Hồ sơ: tên 1–50 ký tự, timezone hợp lệ ở service; chỉ trường cho phép được sửa. `version = expected_version` trước khi tăng version.
- Settings update và sự kiện thay đổi analytics commit cùng nhau; thông báo hoạt động chỉ là preference, không được tắt email xác minh/khôi phục.
- Consent: chủ chỉ SELECT; RPC ghi kiểm tra loại/phiên bản, khóa tài khoản, đối chiếu `expected_revision` của từng loại rồi tăng revision. Request key đã có chỉ trả biên nhận/trạng thái hiện hành, không áp lại ý định cũ; không UPDATE/DELETE trực tiếp.
- Request xuất: chủ chỉ SELECT các trường công khai; tạo qua RPC/backend, không tự đặt trạng thái/path/lease. Worker ghi qua quyền server hẹp.
- RLS theo owner; mọi RPC kiểm tra `auth.uid()`, tombstone xóa và quyền trường. Đóng quyền ghi trực tiếp tương tự [transaction cốt lõi](transaction.md).
- Index theo owner, thời gian tạo và trạng thái/available_at cho hàng đợi; index theo hạn hết file để tác vụ dọn đọc được theo lô.

## Vòng đời

- Bucket `account-exports` private; chỉ worker ghi, API đọc đúng file của yêu cầu được cấp phép. Đề xuất xóa file sau 24 giờ, giữ trạng thái hết hạn tối đa 30 ngày rồi dọn.
- Lease token đóng vai trò fencing token: worker hết lease không được commit hoặc ghi đè kết quả của worker mới; object path có attempt ID và dọn output thừa. Worker ghi ready chỉ nếu request vẫn running, token còn đúng và tài khoản chưa xóa.
- Xóa tài khoản bao gồm settings, consent, bản xuất và file của mọi attempt; không cascade mất manifest trước khi quét xong Storage.
- Yêu cầu xuất và hỗ trợ xuất trong JSON chỉ gồm các trường cho user thấy; trạng thái nội bộ/lease/object path không được lộ.

## Đọc tiếp

- [Vòng đời dữ liệu](vong-doi-du-lieu.md)
- [Backend tài khoản](../backend/tai-khoan-va-cai-dat.md)
