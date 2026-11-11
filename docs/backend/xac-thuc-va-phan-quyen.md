# Closet Loop — Xác thực và phân quyền

[Mục lục](../README.md) · Cập nhật: 11/11/2026

## Xác thực giữa hai ứng dụng

1. Frontend dùng Supabase Auth để đăng nhập và duy trì session.
2. Mỗi request nghiệp vụ gửi access token qua `Authorization: Bearer <token>` tới backend.
3. Dependency xác thực của backend xác minh token với Supabase Auth, ví dụ `auth.get_user(token)`; không chỉ giải mã JWT rồi tin payload. [Tài liệu xác minh người dùng](https://supabase.com/docs/reference/python/auth-getuser).
4. Backend tạo context người dùng cho request và client Supabase theo đúng JWT đó để RLS hoạt động. Không dùng một client đang giữ session mutable dùng chung cho nhiều người.
5. Với tài khoản đang xóa, backend và policy/RPC chặn mutation mới như [vòng đời dữ liệu](../database/vong-doi-du-lieu.md); token hợp lệ không bỏ qua trạng thái này.

Backend nhận Bearer token, không phụ thuộc cookie chéo domain của frontend. CORS khai báo rõ origin frontend, method và header `Authorization`/`Content-Type`; CORS không thay thế xác thực. Cấu hình theo [hướng dẫn FastAPI](https://fastapi.tiangolo.com/tutorial/cors/). Frontend Server Components chuyển token ở server; token không được ghi vào log hoặc URL.

Response headers cần browser đọc (`Retry-After`, `Content-Disposition`, `X-Request-ID` nếu có) phải nằm trong `expose_headers`; request ID cũng có trong body lỗi theo hợp đồng chung.

## Quyền MVP

| Đối tượng | Chủ sở hữu | Tài khoản khác/khách |
| --- | --- | --- |
| Hồ sơ riêng | Đọc và sửa trường cho phép | Không truy cập |
| Món, outfit, lịch | Đọc/ghi dữ liệu của mình theo quy tắc | Không truy cập |
| Log đã mặc | Đọc; thay đổi qua function được kiểm soát | Không truy cập |
| Ảnh | Upload vào vị trí được cấp quyền, đọc ảnh của mình | Không truy cập |
| Job AI | Xem job của mình, gửi yêu cầu xử lý | Không đọc hoặc sửa job của người khác |
| Cài đặt/chấp thuận | Đọc, đổi trường/trạng thái qua API/RPC cho phép | Không truy cập |
| Bản xuất JSON | Tạo/xem/tải yêu cầu của mình còn hạn | Không truy cập |
| Thông báo/phiếu hỗ trợ | Chỉ dữ liệu của mình; không tự tạo thông báo/đổi trạng thái phiếu | Không truy cập |

- Bật RLS trên tất cả bảng có dữ liệu người dùng, gồm bảng liên kết; viết policy cho từng thao tác cần thiết.
- Với xử lý thông thường, dùng session người gọi; không dùng service role làm client mặc định.
- Secret/service role chỉ ở server cho tác vụ quản trị thật sự, ví dụ xóa tài khoản; không đặt trong biến `NEXT_PUBLIC_*`.
- Mutation kiểm tra session, quyền đối tượng và payload. Không coi việc ẩn nút là kiểm soát quyền.
- Kiểm tra phân quyền cả khi sửa mã món/outfit/asset/job trong request.
- Auth user phải có email đã xác minh; profile tạo qua bootstrap có transaction. Client không tự cấp role hoặc sửa trạng thái xóa trong metadata.
- Logout thu hồi refresh token; JWT đã phát có thể còn hiệu lực tới hạn. Chọn hạn JWT phù hợp và không hứa logout làm vô hiệu tức thì mọi bản token/ảnh đã tải. Tombstone xóa vẫn chặn mutation ở database/backend. [Scope đăng xuất](https://supabase.com/docs/guides/auth/signout).
- Thao tác xóa xác minh lại mật khẩu bằng client Auth tạm riêng; chi tiết ở [backend tài khoản](tai-khoan-va-cai-dat.md). Công cụ hỗ trợ dùng quyền vận hành riêng có MFA, không nhận service key trong browser.

Bucket private yêu cầu kiểm soát truy cập khi tải ảnh; bucket public cho phép người có URL xem ảnh. Vì vậy không chuyển cả bucket tủ đồ sang public để làm tính năng chia sẻ. [Mô hình bucket Supabase](https://supabase.com/docs/guides/storage/buckets/fundamentals).

## Mở rộng quyền ở giai đoạn 3–4

- Bestie: thêm `friendships`, `closet_grants`, `closet_grant_items`, `outfit_suggestions` khi triển khai.
- Grant có `owner_id`, `recipient_id`, `expires_at`, `revoked_at` và danh sách món. Mọi lần đọc món/ảnh đều kiểm tra hiệu lực; không cấp quyền sửa đồ gốc.
- Với ảnh chia sẻ cần thu hồi cho lần tải tiếp theo ngay lập tức, dùng endpoint proxy kiểm tra grant mỗi request, phản hồi `private, no-store`; không phát signed URL sống lâu cho người nhận. Ảnh đã tải hoặc chụp lại không thể thu hồi.
- Gợi ý từ bạn chỉ là đề xuất; khi lưu thành outfit riêng phải kiểm tra lại các món và quyền. Preview cũng không được chứa ảnh ngoài phạm vi grant.
- Public Pass: thêm hồ sơ công khai tối thiểu và `pass_listings`; tạo dữ liệu/ảnh công khai riêng đã được người dùng duyệt. Truy vấn công khai chỉ trả trường được phép.
- Khi ẩn bài pass, chặn lần đọc mới và xử lý bản ảnh công khai/cache; không hứa xóa được nội dung người khác đã lưu.

## Đọc tiếp

- [Vòng đời dữ liệu](../database/vong-doi-du-lieu.md)
- [API](../api/hop-dong.md)
