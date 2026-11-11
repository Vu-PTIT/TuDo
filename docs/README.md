# Closet Loop — Mục lục tài liệu

Cập nhật: **11/11/2026** · Tài liệu chuẩn bị code, chưa phải ứng dụng đã triển khai.

**Đã chốt:** Web responsive trước, mobile app sau; frontend/backend tách riêng; backend dùng **Python + Rust**.

**Đề xuất:** frontend Next.js/TypeScript; Python FastAPI phụ trách API/nghiệp vụ; Rust xử lý ảnh qua PyO3/maturin; PostgreSQL/Auth/Storage trên Supabase.

## Bắt đầu đọc

1. [Tổng quan sản phẩm](san-pham/tong-quan.md) và [phạm vi](san-pham/pham-vi-va-lo-trinh.md).
2. [Quyết định](san-pham/quyet-dinh.md) và [kiến trúc tổng thể](kien-truc/tong-the.md).
3. [Frontend](frontend/cau-truc.md), [Python API](backend/python-api.md), [Rust](backend/rust-xu-ly-anh.md).
4. [Schema](database/mo-hinh-du-lieu.md), [transaction](database/transaction.md), [API](api/hop-dong.md).
5. [Kế hoạch code](trien-khai/ke-hoach-code.md) và [môi trường](trien-khai/moi-truong.md).

**Phần bổ sung cho sản phẩm ra mắt thực tế:** bắt đầu ở [tài khoản](san-pham/tai-khoan-va-dang-nhap.md), [cài đặt](san-pham/cai-dat.md), [quyền riêng tư](san-pham/quyen-rieng-tu.md) và [điều kiện ra mắt](trien-khai/san-sang-ra-mat.md). Đây là phạm vi cần triển khai, chưa phải tính năng đã có mã nguồn.

## Sản phẩm

Mục tiêu, phạm vi, chức năng, hành trình và quyết định.

- [Tổng quan sản phẩm](san-pham/tong-quan.md)
- [Phạm vi và lộ trình](san-pham/pham-vi-va-lo-trinh.md)
- [Chức năng MVP](san-pham/chuc-nang-mvp.md)
- [Tài khoản và đăng nhập](san-pham/tai-khoan-va-dang-nhap.md)
- [Hướng dẫn bắt đầu và hồ sơ](san-pham/bat-dau-va-ho-so.md)
- [Cài đặt](san-pham/cai-dat.md)
- [Thông báo](san-pham/thong-bao.md)
- [Quyền riêng tư và dữ liệu cá nhân](san-pham/quyen-rieng-tu.md)
- [Trợ giúp và hỗ trợ](san-pham/ho-tro.md)
- [Hành trình người dùng](san-pham/hanh-trinh.md)
- [Kinh doanh và đo lường](san-pham/kinh-doanh-va-do-luong.md)
- [Quyết định và giả định](san-pham/quyet-dinh.md)

## Kiến trúc

Vai trò các phần và cấu trúc repository.

- [Kiến trúc tổng thể](kien-truc/tong-the.md)
- [Cấu trúc repository](kien-truc/cau-truc-repository.md)

## Frontend

Next.js, feature và component UI.

- [Cấu trúc frontend](frontend/cau-truc.md)
- [Component và trạng thái UI](frontend/component-va-trang-thai.md)

## Backend

Python API, Rust xử lý ảnh, xác thực và AI.

- [Backend Python và API](backend/python-api.md)
- [Backend Rust xử lý ảnh](backend/rust-xu-ly-anh.md)
- [Xác thực và phân quyền](backend/xac-thuc-va-phan-quyen.md)
- [Tài khoản, cài đặt và bản sao dữ liệu](backend/tai-khoan-va-cai-dat.md)
- [Thông báo và hỗ trợ](backend/thong-bao-va-ho-tro.md)
- [Upload ảnh và AI](backend/upload-va-ai.md)

## Database

Schema, transaction và vòng đời dữ liệu.

- [Mô hình dữ liệu](database/mo-hinh-du-lieu.md)
- [Dữ liệu tài khoản và cài đặt](database/tai-khoan-va-cai-dat.md)
- [Dữ liệu thông báo và hỗ trợ](database/thong-bao-va-ho-tro.md)
- [Transaction và ràng buộc](database/transaction.md)
- [Vòng đời dữ liệu và ảnh](database/vong-doi-du-lieu.md)

## API

Endpoint và request/response.

- [Hợp đồng HTTP API](api/hop-dong.md)
- [API tài khoản, cài đặt và bản sao dữ liệu](api/tai-khoan-va-cai-dat.md)
- [API thông báo và hỗ trợ](api/thong-bao-va-ho-tro.md)

## Thiết kế

Token, điều hướng, responsive và bố cục.

- [Hệ thống thiết kế](thiet-ke/he-thong-thiet-ke.md)
- [Điều hướng và responsive](thiet-ke/dieu-huong.md)
- [Bố cục tài khoản và hướng dẫn bắt đầu](thiet-ke/tai-khoan.md)
- [Bố cục cài đặt và hồ sơ](thiet-ke/cai-dat-va-ho-so.md)
- [Bố cục thông báo và hỗ trợ](thiet-ke/thong-bao-va-ho-tro.md)
- [Bố cục màn hình](thiet-ke/bo-cuc-man-hinh.md)
- [Bố cục Outfit Studio](thiet-ke/outfit-studio.md)

## Triển khai

Code, kiểm thử, build, vận hành và mobile.

- [Kế hoạch code](trien-khai/ke-hoach-code.md)
- [Môi trường phát triển và build](trien-khai/moi-truong.md)
- [Kế hoạch kiểm thử](trien-khai/kiem-thu.md)
- [Phát hành và vận hành](trien-khai/phat-hanh-va-van-hanh.md)
- [Email và tác vụ nền](trien-khai/email-va-tac-vu-nen.md)
- [Điều kiện sẵn sàng ra mắt](trien-khai/san-sang-ra-mat.md)
- [Mở rộng sang mobile](trien-khai/mobile.md)

## Cách cập nhật

- Mỗi file quản lý một chủ đề; dùng liên kết để đọc phần liên quan.
- Nghiệp vụ theo tài liệu sản phẩm; transaction/quyền theo database/backend; UI theo thư mục thiết kế.
- Ngôn ngữ backend đã chốt. Framework, phiên bản, nhà cung cấp AI và cấu hình chi tiết cần chốt khi triển khai.
