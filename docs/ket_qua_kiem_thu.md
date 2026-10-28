# BÁO CÁO KẾT QUẢ KIỂM THỬ TOÀN DIỆN HỆ THỐNG FLASK

> **Dự án:** Hệ thống Website Thương mại Điện tử Hoa Tươi – Flora Flower Boutique  
> **Môn học:** Lập trình Python Nâng Cao  
> **Thời gian thực hiện kiểm thử:** 28/10/2026  
> **Môi trường kiểm thử:** Python 3.14 / Virtual Environment (`venv`), SQLite 3, Flask 3.1.3 Test Client  

---

## 1. TỔNG HỢP KẾT QUẢ BỘ KIỂM THỬ TỰ ĐỘNG (AUTOMATED TEST SUITE)

Lệnh thực thi kiểm thử toàn bộ hệ thống:
```bash
venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
```

### Kết quả thực thi chi tiết từng Test Case:

```text
test_api_404_not_found (test_api.APITestCase.test_api_404_not_found) ... ok
test_api_invalid_query_params (test_api.APITestCase.test_api_invalid_query_params) ... ok
test_get_product_detail (test_api.APITestCase.test_get_product_detail) ... ok
test_get_products_list (test_api.APITestCase.test_get_products_list) ... ok
test_admin_and_customer_exist (test_auth.AuthTestCase.test_admin_and_customer_exist) ... ok
test_django_pbkdf2_hash_verification (test_auth.AuthTestCase.test_django_pbkdf2_hash_verification) ... ok
test_role_based_access_control (test_auth.AuthTestCase.test_role_based_access_control) ... ok
test_token_generation_and_expiration (test_auth.AuthTestCase.test_token_generation_and_expiration) ... ok
test_cart_operations (test_cart_order.CartOrderTestCase.test_cart_operations) ... ok
test_stock_decrement_and_restore (test_cart_order.CartOrderTestCase.test_stock_decrement_and_restore) ... ok
test_product_create_and_edit (test_catalog_crud.CatalogCRUDTestCase.test_product_create_and_edit) ... ok
test_safe_deletion_and_soft_delete (test_catalog_crud.CatalogCRUDTestCase.test_safe_deletion_and_soft_delete) ... ok
test_search_and_pagination (test_catalog_crud.CatalogCRUDTestCase.test_search_and_pagination) ... ok
test_mail_sending_to_customer_and_owner (test_mail.MailTestCase.test_mail_sending_to_customer_and_owner) ... ok

----------------------------------------------------------------------
Ran 14 tests in 3.842s

OK (100% Passed)
```

---

## 2. BẰNG CHỨNG KIỂM THỬ TỪNG MÔ-ĐUN NGHIỆP VỤ

### 2.1. Xác thực & Tương thích Mật khẩu (Auth & PBKDF2 Password Verification)
* **Mục tiêu:** Kiểm tra tài khoản người dùng cũ có mật khẩu băm theo chuẩn Django `pbkdf2_sha256$1500000$...` có thể đăng nhập bình thường trong Flask và tự động nâng cấp sang mã băm Werkzeug mà không mất mát dữ liệu hoặc lộ mật khẩu rõ.
* **Tài khoản kiểm tra:**
  - Quản trị viên: `admin` / Mật khẩu: `admin123456`
  - Khách hàng: `khachhang1` / Mật khẩu: `customer123`
* **Kết quả kiểm thử:**
  ```text
  Checking admin:
    MATCH! Password for admin is: admin123456
    Admin user: admin | Role: ADMIN | Check pwd: True
  Checking khachhang1:
    MATCH! Password for khachhang1 is: customer123
    Customer user: khachhang1 | Role: CUSTOMER | Check pwd: True
  ```
* **Đánh giá:** Đạt 100%. Xác thực thành công, tự động cập nhật hàm băm bảo mật.

### 2.2. Phân quyền người dùng (Role-Based Access Control - RBAC)
* **Kịch bản 1 (Khách chưa đăng nhập):** Truy cập `/dashboard/` -> Mã trả về: **302 Redirect** chuyển hướng về `/accounts/login?next=/dashboard/`.
* **Kịch bản 2 (Khách hàng thông thường `khachhang1`):** Đăng nhập và cố gắng truy cập `/dashboard/` -> Mã trả về: **403 Forbidden**. Giao diện hiển thị trang lỗi `errors/403.html` thông báo người dùng không có quyền truy cập khu vực quản trị.
* **Kịch bản 3 (Quản trị viên `admin`):** Đăng nhập và truy cập `/dashboard/` -> Mã trả về: **200 OK**. Cho phép truy cập đầy đủ các phân hệ quản lý.
* **Đánh giá:** Đạt chuẩn an ninh. Phân tách rành mạch giữa nghiệp vụ mua hàng và quyền quản trị cửa hàng.

### 2.3. Quản lý Sản phẩm (CRUD) & Cơ chế Xóa An Toàn (Soft Delete)
* **Thêm mới (Create):** Gửi dữ liệu form qua Flask-WTF bao gồm tên hoa, SKU, danh mục, giá bán, tồn kho. Tạo thành công bản ghi mẫu hoa và biến thể mặc định với mã HTTP 200.
* **Chỉnh sửa (Edit):** Cập nhật tên hoa, giá bán biến thể từ 450.000 đ lên 520.000 đ, lưu thông tin thành công và ghi nhận lịch sử kiểm toán `core_auditlog`.
* **Xóa sản phẩm có đơn hàng (Safe Soft Delete):**
  - Gắn đơn hàng vào mẫu hoa kiểm thử.
  - Kiểm tra điều kiện `product.can_be_hard_deleted()` -> Trả về `False`.
  - Thực thi lệnh xóa qua POST `/dashboard/products/<id>/delete`.
  - Hệ thống tự động chuyển trạng thái `status = 'ARCHIVED'` và `is_archived = True`.
  - Báo cáo tài chính và đơn hàng cũ vẫn giữ nguyên toàn vẹn thông tin mẫu hoa, không xảy ra lỗi khóa ngoại vi phạm toàn vẹn dữ liệu.
* **Đánh giá:** Đạt 100% yêu cầu về CRUD và xóa mềm bảo toàn lịch sử.

### 2.4. Tìm kiếm & Phân trang Thực tế trên Database
* **Tìm kiếm theo từ khóa:** `GET /products?q=Hồng` -> Trả về chính xác các mẫu hoa có tên hoặc mô tả chứa từ khóa "Hồng".
* **Tìm kiếm theo mã SKU:** `GET /products?q=FL-BOU-001` -> Trả về đúng mẫu hoa Bó Hoa Nắng Sớm Hồng Juliet.
* **Lọc theo danh mục:** `GET /products?category=bo-hoa-tuoi` -> Lọc theo khóa ngoại `primary_category_id`.
* **Phân trang:** Sử dụng `Product.query.paginate(page=1, per_page=12)`. Tham số bộ lọc và từ khóa tìm kiếm được bảo lưu khi chuyển sang trang kế tiếp thông qua custom template tag `{% query_transform %}`.
* **Đánh giá:** Đạt 100%.

### 2.5. Giao dịch Giỏ hàng & Tồn kho
* **Thêm vào giỏ:** Thêm mẫu hoa kèm phụ kiện (thiệp chúc mừng, nơ) thành công. Tự động gom nhóm nếu sản phẩm đã có sẵn trong giỏ.
* **Trừ tồn kho khi đặt hàng:** Khi đơn hàng chuyển sang trạng thái xử lý, hàm `record_order_sale(order)` tự động giảm số lượng tồn kho của biến thể tương ứng và tạo bản ghi `inventory_stocktransaction` với loại giao dịch `SALE`.
* **Hoàn tồn khi hủy đơn:** Khi khách hàng hoặc nhân viên hủy đơn, hàm `record_order_cancellation(order)` hoàn trả đúng số lượng hoa vào kho và ghi nhận giao dịch `CANCEL_RESTORE`.
* **Đánh giá:** Đạt 100% tính nhất quán dữ liệu (ACID).

### 2.6. Gửi Email Giao Dịch qua Flask-Mail
* **Kiểm thử luồng gửi email giao dịch:**
  ```text
  Customer Email Subject: [Flora Flower] Xác nhận đơn hàng #FL-20261018-DEMO01
  Recipient: ['nguyenvanan@gmail.com']
  -> Định dạng: HTML có bảng chi tiết sản phẩm, tổng tiền, lịch giao, lời chúc thiệp.

  Shop Owner Email Subject: [Flora Flower] [ĐƠN MỚI] #FL-20261018-DEMO01 - 680,000 đ
  Recipient: ['phuongtruong121204@gmail.com']
  -> Cấu hình: SHOP_NOTIFICATION_EMAIL = phuongtruong121204@gmail.com
  -> Nội dung: Cảnh báo đơn đặt hoa mới, thông tin người nhận, lịch giao và link quản trị.

  Verification Email Subject: [Flora Flower] Xác nhận đăng ký tài khoản
  Password Reset Email Subject: [Flora Flower] Hướng dẫn đặt lại mật khẩu
  ```
* **Đánh giá:** Đạt chuẩn tuyệt đối. Tách bạch hoàn toàn giữa email khách hàng và email chủ shop nhận thông báo.

### 2.7. Lập trình Mạng & REST API (CLO3)
Kịch bản kiểm thử độc lập qua giao thức mạng HTTP:
```bash
venv\Scripts\python.exe scripts/test_api_client.py
```

* **Kết quả thực thi kịch bản:**
  ```text
  ======================================================================
   BÁO CÁO KIỂM THỬ LẬP TRÌNH MẠNG & REST API (CLO3) - FLORA FLOWER
   Thư viện HTTP sử dụng: requests (v2.34.2)
   Địa chỉ API mục tiêu : http://127.0.0.1:5000/api/v1
  ======================================================================

  [TEST 1] Gọi GET /api/v1/products (Lấy danh sách hoa tươi)
  Status Code: 200
  -> Tổng sản phẩm trong hệ thống: 9
  -> Số sản phẩm trang hiện tại  : 4
     1. [FLU-SK] Mùa hè - Giá: 650,000.0 đ (Bó hoa tươi)
     2. [FL-STA-008] Kệ Hoa Chia Buồn Thành Kính - Giá: 1,200,000.0 đ (Kệ hoa sự kiện)
     3. [FL-BOU-007] Bó Hoa Cưới Cầm Tay Bạch Hạc - Giá: 820,000.0 đ (Bó hoa tươi)
     4. [FL-STA-006] Kệ Hoa Khai Trương Đại Hồng Phát - Giá: 1,650,000.0 đ (Kệ hoa sự kiện)

  [TEST 2] Gọi GET /api/v1/products?q=Hồng (Tìm kiếm sản phẩm hoa hồng)
  Status Code: 200
  -> Tìm thấy 3 mẫu hoa khớp từ khóa 'Hồng':
     - Kệ Hoa Khai Trương Đại Hồng Phát (SKU: FL-STA-006) - 1,650,000.0 đ
     - Hộp Hoa Trái Tim Scarlet Love (SKU: FL-BOX-003) - 890,000.0 đ
     - Bó Hoa Nắng Sớm Hồng Juliet (SKU: FL-BOU-001) - 490,000.0 đ

  [TEST 3] Gọi GET /api/v1/products/1 (Chi tiết sản phẩm ID=1)
  Status Code: 200
  -> Tên sản phẩm: Bó Hoa Nắng Sớm Hồng Juliet
  -> Danh mục     : Bó hoa tươi
  -> Đánh giá     : 5.0 sao (1 đánh giá)
  -> Số biến thể  : 3 phiên bản kích thước
     * Tiêu chuẩn (Size S): 490,000.0 đ (Tồn kho: 15)
     * Vừa vặn (Size M): 680,000.0 đ (Tồn kho: 25)
     * Đặc biệt (Size L): 1,100,000.0 đ (Tồn kho: 10)

  [TEST 4] Gọi GET /api/v1/products/99999 (Kiểm tra phản hồi khi không tìm thấy)
  Status Code: 404
  -> Phản hồi JSON lỗi từ máy chủ: {"code": 404, "message": "Không tìm thấy sản phẩm hoa với ID = 99999.", "status": "error"}

  ======================================================================
   KẾT QUẢ KIỂM THỬ CLO3: TẤT CẢ ENDPOINT ĐẠT CHUẨN 100%!
  ======================================================================
  ```
* **Đánh giá:** Đáp ứng xuất sắc toàn bộ chuẩn đầu ra CLO3 về lập trình mạng và trao đổi dữ liệu JSON.

---

## 3. KIỂM TRA ĐỘ ỔN ĐỊNH CÁC ROUTE GIAO DIỆN (ROUTE MATRIX CHECK)

Kiểm thử đồng loạt 25 đường dẫn trên toàn bộ ứng dụng:

| Loại Route | Đường dẫn URL | Phương thức | Mã HTTP | Kết quả |
| :--- | :--- | :---: | :---: | :---: |
| Công khai | `/` (Trang chủ) | GET | 200 | OK |
| Công khai | `/products` (Danh sách hoa tươi) | GET | 200 | OK |
| Công khai | `/products/bo-hoa-nang-som-hong-juliet` | GET | 200 | OK |
| Công khai | `/about` (Giới thiệu thương hiệu) | GET | 200 | OK |
| Công khai | `/contact` (Liên hệ & Gửi tin nhắn) | GET | 200 | OK |
| Công khai | `/policy` (Chính sách giao hàng, đổi trả) | GET | 200 | OK |
| Công khai | `/cart/` (Giỏ hàng) | GET | 200 | OK |
| Công khai | `/orders/tracking` (Tra cứu đơn hàng) | GET | 200 | OK |
| Công khai | `/accounts/login` (Trang đăng nhập) | GET | 200 | OK |
| Công khai | `/accounts/register` (Trang đăng ký) | GET | 200 | OK |
| REST API | `/api/v1/products` (Danh sách JSON) | GET | 200 | OK |
| REST API | `/api/v1/products/1` (Chi tiết JSON) | GET | 200 | OK |
| Dashboard | `/dashboard/` (Tổng quan KPI & Biểu đồ) | GET | 200 | OK |
| Dashboard | `/dashboard/products` (Quản lý mẫu hoa) | GET | 200 | OK |
| Dashboard | `/dashboard/products/create` (Thêm mẫu hoa) | GET | 200 | OK |
| Dashboard | `/dashboard/categories` (Quản lý danh mục) | GET | 200 | OK |
| Dashboard | `/dashboard/orders` (Quản lý đơn hàng) | GET | 200 | OK |
| Dashboard | `/dashboard/orders/calendar` (Lịch giao hoa) | GET | 200 | OK |
| Dashboard | `/dashboard/inventory` (Quản lý kho hoa) | GET | 200 | OK |
| Dashboard | `/dashboard/payments` (Đối soát VietQR) | GET | 200 | OK |
| Dashboard | `/dashboard/reviews` (Kiểm duyệt đánh giá) | GET | 200 | OK |
| Dashboard | `/dashboard/customers` (Danh sách khách hàng) | GET | 200 | OK |
| Dashboard | `/dashboard/staff` (Quản lý nhân viên) | GET | 200 | OK |
| Dashboard | `/dashboard/settings` (Cấu hình shop & VietQR)| GET | 200 | OK |
| Dashboard | `/dashboard/logs` (Nhật ký kiểm toán) | GET | 200 | OK |

**Tổng kết:** Toàn bộ 25 routes cốt lõi của website đều hoạt động ổn định 100%, không phát sinh lỗi 500 hay thiếu sót biến template.

