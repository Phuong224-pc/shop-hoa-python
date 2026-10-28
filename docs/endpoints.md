# SƠ ĐỒ ĐƯỜNG DẪN HỆ THỐNG (ENDPOINTS & ROUTING DIRECTORY)

Hệ thống **FLORA FLOWER** được xây dựng trên nền tảng **Flask Web Framework** theo cấu trúc **8 Blueprints** độc lập, tuân thủ nguyên tắc định tuyến RESTful và phân tách rõ ràng giữa phân hệ Khách hàng (Storefront), Cổng Quản trị (Dashboard) và Cổng Lập trình mạng REST API (CLO3).

---

## 1. Phân Hệ Cửa Hàng & Mua Hoa (Blueprint `catalog` & `main`)

| URL Pattern | Method | Endpoint / Function | Phân Quyền | Chức Năng Nghiệp Vụ |
| :--- | :---: | :--- | :---: | :--- |
| `/` | `GET` | `main.home` | Công khai | Trang chủ: Banner slider hoa tươi, danh mục nổi bật, hoa thịnh hành, cam kết chất lượng. |
| `/products/` | `GET` | `catalog.product_list` | Công khai | Danh mục sản phẩm: Bộ lọc theo kiểu dáng, dịp tặng, loài hoa, khoảng giá, sắp xếp và phân trang. |
| `/products/<slug>/` | `GET` | `catalog.product_detail` | Công khai | Chi tiết mẫu hoa: Chọn size S/M/L, cập nhật giá và tồn kho tức thời, phụ kiện bán kèm, đánh giá. |
| `/categories/<slug>/` | `GET` | `catalog.category_detail` | Công khai | Danh sách mẫu hoa theo danh mục kiểu dáng cụ thể (Bó hoa, Giỏ hoa, Kệ hoa...). |
| `/occasions/<slug>/` | `GET` | `catalog.occasion_detail` | Công khai | Danh sách mẫu hoa theo dịp tặng (Sinh nhật, Khai trương, Tình yêu, Cưới, Chia buồn). |
| `/api/variants/<id>/` | `GET` | `catalog.variant_detail_api` | Công khai | API lấy thông tin giá, SKU, tồn kho của biến thể khi khách đổi kích cỡ trên giao diện. |

---

## 2. Phân Hệ Giỏ Hàng & Mã Giảm Giá (Blueprint `cart`)

| URL Pattern | Method | Endpoint / Function | Phân Quyền | Chức Năng Nghiệp Vụ |
| :--- | :---: | :--- | :---: | :--- |
| `/cart/` | `GET` | `cart.cart_detail` | Công khai | Xem giỏ hàng, danh sách hoa đã chọn, phụ kiện đính kèm, thanh tiến trình freeship, tạm tính. |
| `/cart/add/` | `POST` | `cart.cart_add` | Công khai | Thêm mẫu hoa vào giỏ (chọn biến thể S/M/L, số lượng, lời chúc thiệp và phụ kiện đi kèm). |
| `/cart/items/<int:item_id>/update` | `POST` | `cart.update_cart_item` | Công khai | Tăng/giảm số lượng từng dòng sản phẩm trong giỏ hàng. |
| `/cart/items/<int:item_id>/remove` | `POST` | `cart.remove_cart_item` | Công khai | Xóa một dòng sản phẩm khỏi giỏ hàng. |
| `/cart/apply-coupon/` | `POST` | `cart.apply_coupon` | Công khai | Kiểm tra điều kiện và áp dụng mã voucher ưu đãi vào giỏ hàng. |
| `/cart/remove-coupon/` | `POST` | `cart.remove_coupon` | Công khai | Hủy áp dụng mã voucher hiện tại. |

---

## 3. Phân Hệ Đặt Hàng, Thanh Toán & Tra Cứu (Blueprint `orders`)

| URL Pattern | Method | Endpoint / Function | Phân Quyền | Chức Năng Nghiệp Vụ |
| :--- | :---: | :--- | :---: | :--- |
| `/orders/checkout/` | `GET`, `POST` | `orders.checkout` | Khách hàng | Màn hình thanh toán: Tách người đặt vs người nhận, chọn ngày & khung giờ giao, thiệp chúc mừng, ẩn danh, COD/VietQR. Chặn nhân viên đặt đơn. |
| `/orders/success/<order_number>/` | `GET` | `orders.order_success` | Công khai | Màn hình hoàn tất đơn: Hiển thị mã đơn, tóm tắt và sinh mã VietQR chuyển khoản tự động. Kích hoạt Flask-Mail gửi email cho khách và shop. |
| `/orders/tracking/` | `GET`, `POST` | `orders.order_tracking` | Công khai | Tra cứu tiến độ đơn hàng nhanh không cần đăng nhập bằng Mã đơn + Số điện thoại người đặt. |
| `/orders/<int:pk>/` | `GET` | `orders.order_detail` | Khách đặt đơn | Xem chi tiết đơn hàng, dòng thời gian trạng thái, tải hóa đơn, tải ảnh biên lai thanh toán. |
| `/orders/<int:pk>/cancel/` | `POST` | `orders.order_cancel` | Khách đặt đơn | Khách hàng tự hủy đơn (chỉ cho phép khi đơn chưa chuyển sang cắm hoa), hoàn kho tự động. |
| `/orders/<int:pk>/reorder/` | `POST` | `orders.reorder` | Khách đặt đơn | Mua lại đơn cũ: tự động thêm toàn bộ sản phẩm và phụ kiện của đơn cũ vào giỏ hàng hiện tại. |
| `/orders/<int:order_id>/review/<int:product_id>/` | `POST` | `reviews.submit_review` | Khách đã mua | Viết đánh giá số sao và nhận xét cho mẫu hoa đã nhận thành công (Verified Purchase). |
| `/payments/<int:pk>/upload-proof/` | `POST` | `orders.upload_proof` | Khách đặt đơn | Tải ảnh chụp biên lai chuyển khoản VietQR cho giao dịch. |

---

## 4. Phân Hệ Tài Khoản & Phân Quyền (Blueprint `auth`)

| URL Pattern | Method | Endpoint / Function | Phân Quyền | Chức Năng Nghiệp Vụ |
| :--- | :---: | :--- | :---: | :--- |
| `/accounts/register/` | `GET`, `POST` | `auth.register` | Chưa login | Đăng ký tài khoản khách hàng mới (kiểm tra email, username trùng, băm mật khẩu an toàn). |
| `/accounts/login/` | `GET`, `POST` | `auth.login` | Chưa login | Đăng nhập tài khoản (hỗ trợ xác minh mật khẩu Django cũ, tự nâng cấp lên Werkzeug hash; tự gộp giỏ hàng session). |
| `/accounts/logout/` | `POST` | `auth.logout` | Đã login | Đăng xuất an toàn khỏi hệ thống qua Flask-Login. |
| `/accounts/profile/` | `GET`, `POST` | `auth.profile` | Đã login | Quản lý hồ sơ cá nhân: Họ tên, số điện thoại, email, cập nhật thông tin. |
| `/accounts/addresses/` | `GET`, `POST` | `auth.addresses` | Khách hàng | Quản lý danh sách sổ địa chỉ nhận hoa thân quen. |
| `/accounts/addresses/<int:id>/delete/` | `POST` | `auth.address_delete` | Khách hàng | Xóa một địa chỉ nhận hàng khỏi sổ tay. |
| `/accounts/my-orders/` | `GET` | `auth.my_orders` | Khách hàng | Xem danh sách toàn bộ các đơn hàng đã đặt trong lịch sử. |
| `/accounts/wishlist/` | `GET` | `auth.wishlist` | Khách hàng | Xem danh sách các mẫu hoa yêu thích đã lưu. |
| `/accounts/wishlist/toggle/<int:product_id>/` | `POST` | `auth.wishlist_toggle` | Khách hàng | API thêm/xóa nhanh mẫu hoa vào danh sách yêu thích (AJAX). |
| `/accounts/password-change/` | `GET`, `POST` | `auth.password_change` | Đã login | Đổi mật khẩu tài khoản (yêu cầu mật khẩu cũ chính xác). |

---

## 5. Phân Hệ Lập Trình Mạng & REST API (Blueprint `api` - CLO3)

| URL Pattern | Method | Endpoint / Function | Phân Quyền | Định Dạng & Chức Năng |
| :--- | :---: | :--- | :---: | :--- |
| `/api/v1/products` | `GET` | `api.get_products` | Công khai | JSON: Danh sách sản phẩm hoa tươi. Hỗ trợ query string tìm kiếm `?q=...`, lọc danh mục `?category_id=...`, lọc dịp `?occasion_id=...`, sắp xếp `?sort=...` và phân trang `?page=...&per_page=...`. |
| `/api/v1/products/<int:id>` | `GET` | `api.get_product_detail` | Công khai | JSON: Chi tiết đầy đủ của một mẫu hoa theo ID. Trả về tên, mô tả, danh mục, toàn bộ biến thể kích thước S/M/L kèm tồn kho, đánh giá khách hàng. Trả về mã lỗi 404 khi không tìm thấy. |

---

## 6. Phân Hệ Quản Trị Vận Hành (Blueprint `dashboard`)
*Yêu cầu quyền hạn nhân viên (`role in ['ADMIN', 'STAFF']`). Khách hàng truy cập bị từ chối 403 Forbidden.*

| URL Pattern | Method | Endpoint / Function | Quyền Hạn | Chức Năng Nghiệp Vụ |
| :--- | :---: | :--- | :---: | :--- |
| `/dashboard/` | `GET` | `dashboard.overview` | Nhân viên | Dashboard tổng quan: Doanh thu thực, đơn hàng, AOV, cảnh báo tồn thấp, biểu đồ Chart.js. |
| `/dashboard/delivery-calendar/` | `GET` | `dashboard.delivery_calendar` | Nhân viên | Lịch giao hoa trực quan theo ngày và 4 khung giờ giao trong ngày. |
| `/dashboard/orders/` | `GET` | `dashboard.order_list` | Nhân viên | Danh sách quản lý đơn hàng, bộ lọc trạng thái và ngày giao hoa. |
| `/dashboard/orders/<int:pk>/detail/` | `GET`, `POST` | `dashboard.order_detail` | Nhân viên | Chi tiết đơn hàng, duyệt trạng thái, ghi chú thợ cắm hoa, cập nhật tiến trình. |
| `/dashboard/orders/<int:pk>/print-bill/` | `GET` | `dashboard.order_print_bill` | Nhân viên | In Hóa đơn giao hàng cho khách hàng (kèm đầy đủ giá tiền và phụ kiện). |
| `/dashboard/orders/<int:pk>/print-florist/`| `GET` | `dashboard.order_print_florist`| Nhân viên | In Phiếu thợ cắm hoa (ẩn tuyệt đối thông tin tiền bạc để bảo mật). |
| `/dashboard/products/` | `GET` | `dashboard.product_list` | Nhân viên | Danh sách sản phẩm hoa, tìm kiếm, phân loại, trạng thái hiển thị, tồn kho. |
| `/dashboard/products/create/` | `GET`, `POST` | `dashboard.product_create` | Nhân viên | Thêm mẫu hoa mới, tạo các biến thể kích thước mặc định qua Flask-WTF. |
| `/dashboard/products/<int:pk>/edit/` | `GET`, `POST` | `dashboard.product_edit` | Nhân viên | Chỉnh sửa thông tin mẫu hoa, quản lý các biến thể S/M/L, ảnh chi tiết. |
| `/dashboard/products/<int:pk>/delete/` | `POST` | `dashboard.product_delete` | Nhân viên | Xóa an toàn mẫu hoa: Tự động chuyển sang Lưu trữ (Soft Delete / Archive) nếu đã có đơn hàng để bảo toàn hóa đơn. |
| `/dashboard/products/<int:product_id>/variants/save/` | `POST` | `dashboard.product_variant_save` | Nhân viên | Thêm mới hoặc cập nhật biến thể kích thước cho sản phẩm. |
| `/dashboard/products/<int:product_id>/variants/<int:variant_id>/delete/` | `POST` | `dashboard.product_variant_delete` | Nhân viên | Xóa biến thể kích thước (chặn xóa nếu là biến thể duy nhất còn lại). |
| `/dashboard/products/<int:pk>/toggle-status/`| `POST` | `dashboard.product_toggle_status`| Nhân viên | Đổi nhanh trạng thái: Hiển thị (PUBLISHED) / Ẩn (DRAFT) / Lưu trữ (ARCHIVED). |
| `/dashboard/categories/` | `GET` | `dashboard.category_list` | Nhân viên | Quản lý danh mục kiểu dáng, dịp tặng, loài hoa chủ đạo. |
| `/dashboard/categories/save/` | `POST` | `dashboard.category_save` | Nhân viên | Thêm hoặc cập nhật danh mục, dịp tặng. |
| `/dashboard/accessories/` | `GET` | `dashboard.accessory_list` | Nhân viên | Quản lý danh sách phụ kiện bán kèm (thiệp, banner, gấu bông). |
| `/dashboard/accessories/save/` | `POST` | `dashboard.accessory_save` | Nhân viên | Thêm mới hoặc cập nhật phụ kiện và giá bán kèm. |
| `/dashboard/inventory/` | `GET` | `dashboard.inventory_list` | Nhân viên | Quản lý kho hoa theo từng biến thể, danh sách cảnh báo tồn kho thấp. |
| `/dashboard/inventory/<int:id>/adjust/` | `POST` | `dashboard.inventory_adjust` | Nhân viên | Điều chỉnh kiểm kê tồn kho thủ công kèm lý do vào sổ cái `StockTransaction`. |
| `/dashboard/inventory/<int:id>/import/` | `POST` | `dashboard.inventory_import` | Nhân viên | Nhập thêm số lượng hoa tươi mới về kho. |
| `/dashboard/payments/` | `GET` | `dashboard.payment_list` | Nhân viên | Quản lý giao dịch thanh toán, danh sách chờ duyệt biên lai VietQR. |
| `/dashboard/payments/<int:pk>/verify/` | `POST` | `dashboard.payment_verify` | Nhân viên | Duyệt biên lai chuyển khoản VietQR hoặc xác nhận thu tiền mặt COD. |
| `/dashboard/customers/` | `GET` | `dashboard.customer_list` | Nhân viên | Danh sách khách hàng, thống kê số đơn đã mua, tổng tiền chi tiêu tích lũy. |
| `/dashboard/customers/<int:pk>/detail/` | `GET` | `dashboard.customer_detail` | Nhân viên | Xem chi tiết hồ sơ khách hàng, danh sách địa chỉ, lịch sử đơn đặt. |
| `/dashboard/staff/` | `GET` | `dashboard.staff_list` | Quản trị viên | Danh sách nhân viên và quản lý phân quyền chức vụ trong cửa hàng. |
| `/dashboard/promotions/` | `GET` | `dashboard.promotion_list` | Nhân viên | Danh sách mã voucher giảm giá và chiến dịch khuyến mãi. |
| `/dashboard/promotions/save/` | `POST` | `dashboard.promotion_save` | Nhân viên | Tạo mới hoặc cập nhật mã ưu đãi. |
| `/dashboard/reviews/` | `GET` | `dashboard.review_list` | Nhân viên | Danh sách đánh giá mẫu hoa từ khách hàng. |
| `/dashboard/reviews/<int:pk>/moderate/` | `POST` | `dashboard.review_moderate` | Nhân viên | Duyệt hiển thị công khai hoặc ẩn đánh giá của khách hàng. |
| `/dashboard/contacts/` | `GET` | `dashboard.contact_message_list`| Nhân viên | Quản lý danh sách tin nhắn liên hệ gửi từ khách hàng. |
| `/dashboard/settings/` | `GET`, `POST` | `dashboard.settings` | Quản trị viên | Cấu hình tên shop, tài khoản nhận VietQR, phí ship, thời gian chuẩn bị hoa. |
| `/dashboard/reports/export/orders/` | `GET` | `dashboard.export_orders_csv` | Nhân viên | Xuất danh sách đơn hàng sang file CSV mã hóa chuẩn UTF-8 BOM cho Microsoft Excel. |
| `/dashboard/logs/` | `GET` | `dashboard.audit_logs` | Nhân viên | Xem lịch sử nhật ký kiểm toán hệ thống. |

---

## 7. Phân Hệ Trang Tĩnh & Nội Dung (Blueprint `main`)

| URL Pattern | Method | Endpoint / Function | Phân Quyền | Chức Năng Nghiệp Vụ |
| :--- | :---: | :--- | :---: | :--- |
| `/about/` | `GET` | `main.about` | Công khai | Giới thiệu về cửa hàng hoa tươi nghệ thuật FLORA FLOWER, triết lý thiết kế. |
| `/contact/` | `GET`, `POST` | `main.contact` | Công khai | Thông tin liên hệ, bản đồ, hotline, form gửi lời nhắn cho cửa hàng qua Flask-WTF. |
| `/policy/` | `GET` | `main.policy` | Công khai | Chính sách giao nhận hoa tươi, chính sách bảo hành hoa tươi và đổi trả. |
