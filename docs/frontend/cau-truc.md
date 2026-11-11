# Closet Loop — Cấu trúc frontend

[Mục lục](../README.md) · Cập nhật: 11/11/2026

Công nghệ đề xuất: **Next.js + React + TypeScript**, Tailwind CSS, shadcn/ui khi cần; Zod kiểm tra form.

## Frontend — trang, chức năng và phần dùng chung

```text
frontend/
├── public/
│   ├── icons/                    # Logo, biểu tượng loại đồ
│   └── images/                   # Ảnh tĩnh có quyền sử dụng
├── src/
│   ├── proxy.ts                  # Refresh session Auth trên Next.js 16+
│   ├── app/                      # Route, layout, loading, error
│   │   ├── layout.tsx
│   │   ├── (auth)/               # Nhóm route không tạo tiền tố URL
│   │   │   ├── login/page.tsx
│   │   │   ├── register/page.tsx
│   │   │   ├── verify-email/page.tsx
│   │   │   ├── forgot-password/page.tsx
│   │   │   └── reset-password/page.tsx
│   │   ├── auth/confirm/route.ts  # Callback xác minh/session Auth
│   │   ├── auth/error/page.tsx
│   │   ├── (public)/            # /, help, terms, privacy, about
│   │   ├── not-found.tsx        # Không tiết lộ đối tượng riêng
│   │   ├── global-error.tsx
│   │   └── (main)/
│   │       ├── layout.tsx        # AppShell cho người đã đăng nhập
│   │       ├── onboarding/page.tsx
│   │       ├── today/page.tsx
│   │       ├── wardrobe/         # Danh sách, thêm, chi tiết, sửa món
│   │       ├── outfits/          # Danh sách, Studio tạo/sửa outfit
│   │       ├── planner/page.tsx
│   │       ├── insights/page.tsx
│   │       ├── notifications/page.tsx
│   │       ├── help/             # contact, requests, requests/[id]
│   │       └── settings/         # Mục lục và trang con từng nhóm
│   │           ├── page.tsx
│   │           ├── profile/page.tsx
│   │           ├── security/page.tsx
│   │           ├── preferences/page.tsx
│   │           ├── notifications/page.tsx
│   │           └── privacy/page.tsx
│   ├── features/                 # UI và thao tác của từng chức năng
│   │   ├── auth/                 # Đăng ký, đăng nhập, khôi phục
│   │   ├── accounts/             # Bootstrap, onboarding, hồ sơ, xóa
│   │   ├── settings/             # Tùy chọn dùng, thông báo, đo lường
│   │   ├── data-exports/         # Yêu cầu xuất và tải JSON riêng
│   │   ├── notifications/        # Danh sách, số chưa đọc, mark-read
│   │   ├── support/              # Form và danh sách phiếu của mình
│   │   ├── today/                # Tổng hợp lịch hôm nay và sắp tới
│   │   ├── wardrobe/             # Tủ đồ, form món, tìm/lọc
│   │   ├── outfits/              # Studio và outfit đã lưu
│   │   ├── planner/              # Lịch, xác nhận/hủy đã mặc
│   │   ├── insights/             # Girl Math, hiển thị CPW
│   │   └── media/                # Chọn ảnh, upload, xem kết quả AI
│   └── shared/
│       ├── components/
│       │   ├── ui/               # Button, input, dialog, sheet
│       │   ├── layout/           # AppShell, sidebar, bottom navigation
│       │   └── feedback/         # EmptyState, ErrorState, loading
│       ├── hooks/                # Hook dùng ở nhiều chức năng
│       ├── lib/
│       │   ├── api/              # HTTP client gửi Bearer token
│       │   └── supabase/         # Client Auth cho browser/server
│       ├── config/               # Biến public, navigation
│       ├── styles/               # Global CSS, token màu/chữ/khoảng cách
│       ├── types/                # Kiểu HTTP chung, phân trang, lỗi API
│       └── utils/                # Định dạng tiền/ngày để hiển thị
├── tests/
│   ├── unit/
│   └── e2e/                      # Playwright gọi cả frontend/backend
├── next.config.ts
└── tsconfig.json
```

**Bên trong một frontend feature**, ví dụ `frontend/src/features/wardrobe/`:

```text
wardrobe/
├── components/
│   ├── WardrobeGrid.tsx          # Lưới món đồ
│   ├── GarmentCard.tsx           # Thẻ một món
│   ├── WardrobeFilters.tsx       # Tìm kiếm và bộ lọc
│   └── ItemForm.tsx              # Thêm/sửa món
├── hooks/
│   └── useWardrobe.ts            # State bộ lọc, tải lại, thao tác UI
├── api/
│   └── wardrobe.api.ts           # Hàm gọi HTTP endpoint Tủ đồ
├── schemas/
│   └── item-form.schema.ts       # Validation form phía người dùng
└── types/
    └── wardrobe.types.ts         # Kiểu hiển thị và kiểu request/response
```

Quy ước tương tự cho `outfits`, `planner`, `accounts`, `media`; feature chỉ đọc như `insights` có thể không cần `schemas/`. `outfits` có thêm reducer/hook cho thao tác bảng phối. Không tạo thư mục trống chỉ để đủ mẫu.

| Nhánh frontend | Đặt nội dung gì ở đây? |
| --- | --- |
| `app/` | Ghép trang từ feature, đọc route params, layout, trạng thái trang |
| `features/<tên>/components/` | Component chỉ thuộc chức năng đó |
| `features/<tên>/hooks/` | State và hành vi UI, gọi lớp `api/` khi cần |
| `features/<tên>/api/` | Request/response HTTP có type; không chứa truy vấn SQL |
| `features/<tên>/schemas/` | Kiểm tra form để phản hồi sớm; backend kiểm tra lại |
| `features/<tên>/types/` | Kiểu UI; kiểu HTTP bám hợp đồng API, không import type database |
| `shared/` | Phần đã thực sự dùng chung giữa các feature |

Supabase Auth cần client browser/server và Proxy refresh cookie theo phiên bản Next.js trong [hướng dẫn SSR](https://supabase.com/docs/guides/auth/server-side/nextjs). Proxy này chỉ phục vụ session frontend. Khóa đặc quyền database, khóa AI và xử lý thư viện Rust `image_core` chỉ nằm trong backend.

`(public)/help/page.tsx` là FAQ công khai; các route `/help/contact`, `/help/requests` trong `(main)` có bảo vệ tài khoản và AppShell. Không tạo trùng hai `page.tsx` cho cùng URL. `/onboarding` cho phép thiếu profile, gọi bootstrap sau chấp nhận; layout không redirect vòng khi user mới chưa được khởi tạo.

Cache dữ liệu riêng khóa theo user ID và xóa khi sign-out/đổi tài khoản. Analytics mặc định chưa bật cho đến khi đọc được lựa chọn ở settings. Callback/recovery và download JSON không đưa token/signed URL vào analytics hoặc cache công khai.

Tham khảo [Next.js App Router](https://nextjs.org/docs/app), [Tailwind cho Next.js](https://tailwindcss.com/docs/installation/framework-guides/nextjs).

## Đọc tiếp

- [API](../api/hop-dong.md)
- [Component](component-va-trang-thai.md)
- [Điều hướng](../thiet-ke/dieu-huong.md)
