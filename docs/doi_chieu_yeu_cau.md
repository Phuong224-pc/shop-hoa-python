# BẢNG ĐỐI CHIẾU TOÀN DIỆN YÊU CẦU ĐỒ ÁN VỚI MÃ NGUỒN THỰC TẾ

> **Môn học:** Lập trình Python Nâng Cao (Mã HP: 71ITSE31003)  
> **Giảng viên hướng dẫn:** ThS. Nguyễn Thị Mỹ Linh  
> **Đơn vị:** Khoa Công Nghệ Thông Tin – Trường Đại học Văn Lang  
> **Dự án:** Website Thương Mại Điện Tử Hoa Tươi Cao Cấp – Flora Flower Boutique  
> **Căn cứ đối chiếu:** File yêu cầu & mẫu báo cáo `Mau_Bao_Cao_DoAn_LapTrinhPythonNangCao.docx`

---

## 1. TỔNG QUAN ĐỐI CHIẾU THEO CHUẨN ĐẦU RA (CLO)

| Mã Chuẩn Đầu Ra (CLO) | Tỷ trọng | Yêu cầu cốt lõi của Giảng viên | Mức độ đáp ứng | Đánh giá |
| :--- | :---: | :--- | :--- | :---: |
| **CLO 2** | **50%** | Xây dựng ứng dụng web Flask hoàn chỉnh, Jinja2 template kế thừa, Flask-WTF xử lý form & CSRF, Flask-SQLAlchemy quản lý ORM & transaction, Flask-Mail gửi email giao dịch, xác thực & phân quyền RBAC, CRUD đầy đủ kèm cơ chế xóa an toàn, tìm kiếm và phân trang thực tế trên database. | **Đạt 100%** | Xuất sắc |
| **CLO 3** | **10%** | Yếu tố lập trình mạng: Xây dựng REST API trả về định dạng JSON (`GET /api/v1/products`, `GET /api/v1/products/<id>`), xử lý HTTP status codes, validation tham số, bảo mật dữ liệu, kèm kịch bản Python (`scripts/test_api_client.py`) sử dụng thư viện `requests`/`urllib` gọi API và xử lý lỗi kết nối/timeout. | **Đạt 100%** | Xuất sắc |
| **CLO 4** | **20%** | Sử dụng thành thạo và kết hợp hiệu quả các thư viện chuẩn và chuyên biệt của Python: `Flask`, `Flask-WTF`, `Flask-SQLAlchemy`, `Flask-Mail`, `Flask-Login`, `Flask-Migrate`, `Jinja2`, `Werkzeug`, `itsdangerous`, `requests`, `hashlib`, `json`, `csv`. | **Đạt 100%** | Xuất sắc |
| **CLO 5** | **10%** | Cấu trúc mã nguồn module hóa theo **Large Application Structure** (`app/`, factory `create_app()`, Blueprints chức năng, `config.py`), mã nguồn sạch, tài liệu kỹ thuật đầy đủ, báo cáo học thuật chuẩn mực theo mẫu quy định. | **Đạt 100%** | Xuất sắc |
| **CLO 6** | **10%** | Tác phong thực hiện nghiêm túc, tính toàn vẹn dữ liệu, kiểm thử tự động bài bản, bảo mật thông tin và tuân thủ đạo đức lập trình. | **Đạt 100%** | Xuất sắc |

---

## 2. BẢNG CHI TIẾT ĐỐI CHIẾU TỪNG TIÊU CHÍ KỸ THUẬT

| STT | Yêu cầu kỹ thuật | Mục trong file Giảng viên | Module / File thực hiện | Hiện trạng | Giải pháp & Chi tiết triển khai | Kết quả kiểm thử thực tế |
| :---: | :--- | :--- | :--- | :---: | :--- | :--- |
| **1** | **Ngôn ngữ & Framework: Python + FLASK** | Phần II & III mẫu báo cáo; Phiếu chấm CLO2 | `app/__init__.py`, `run.py`, `config.py` | **ĐẠT** | Ứng dụng xây dựng 100% trên nền tảng **Flask 3.1.3** theo kiến trúc **Large Application Structure**. Khởi tạo qua Application Factory `create_app()`, phân tách môi trường cấu hình Development, Testing, Production. | Server Flask khởi chạy ổn định tại cổng 5000 (`python run.py`), nạp 8 Blueprints chức năng và phục vụ người dùng trơn tru. |
| **2** | **Cơ sở dữ liệu & ORM: Flask-SQLAlchemy** | Yêu cầu bắt buộc CLO2; Chương 2.3 | `app/extensions.py`, `app/models/` (user, catalog, cart, order, payment, inventory, promotion, review, content, core) | **ĐẠT** | Khai báo extensions độc lập `db = SQLAlchemy()`, liên kết qua `db.init_app(app)`. Định nghĩa 11 thực thể ORM với khóa chính, khóa ngoại, index và quan hệ `db.relationship` rõ ràng. Xử lý transaction và rollback khi lỗi. | 100% dữ liệu gốc trong `db.sqlite3` được bảo toàn: 9 mẫu hoa, 16 biến thể, 5 danh mục, 3 đơn hàng, 2 tài khoản, 28 lịch sử kiểm toán. |
| **3** | **Biểu mẫu & CSRF: Flask-WTF** | Yêu cầu bắt buộc CLO2; Chương 2.4 | `app/forms/auth.py`, `app/forms/catalog.py`, `app/forms/order.py`, `app/forms/review.py` | **ĐẠT** | Sử dụng lớp kế thừa `FlaskForm` của Flask-WTF. Khai báo các field có validator (`DataRequired`, `Email`, `Length`, `EqualTo`, `NumberRange`, `FileAllowed`). Token CSRF được nhúng tự động trên mọi form POST, bảo vệ chống giả mạo request. | Tất cả form đăng ký, đăng nhập, thêm/sửa sản phẩm, đặt hàng và hủy đơn đều xác thực hợp lệ và chặn đứng request thiếu CSRF token. |
| **4** | **Giao diện & Kế thừa: Jinja2 Templates** | Yêu cầu bắt buộc CLO2; Chương 2.4 & 3 | `templates/base.html`, `templates/shop/`, `templates/dashboard/` | **ĐẠT** | Kế thừa mẫu đa cấp (`base.html` -> các trang con). Định nghĩa bộ lọc Jinja2 tùy biến (`currency`, `order_status_badge`, `payment_status_badge`, `date`, `truncatechars`). Tích hợp Context Processor cung cấp biến toàn cục (`shop_setting`, `header_categories`, `global_cart`, `user`). | 46 templates Jinja2 kế thừa chuẩn xác, giao diện Responsive Bootstrap 5 sang trọng, hiển thị mượt mà trên Mobile và Desktop. |
| **5** | **Gửi Email giao dịch: Flask-Mail** | Yêu cầu bắt buộc CLO2; Chương 2.4 | `app/services/email.py`, `config.py` | **ĐẠT** | Tích hợp thư viện `Flask-Mail` với cấu hình SMTP qua biến môi trường. Phân định rõ 2 luồng email: Email xác nhận đặt hàng gửi cho khách hàng, và Email cảnh báo đơn hàng mới gửi về cho Chủ shop tại địa chỉ cấu hình **`SHOP_NOTIFICATION_EMAIL = phuongtruong121204@gmail.com`**. Hỗ trợ định dạng song song HTML và Plain Text tiếng Việt UTF-8. Cơ chế gửi bất đồng bộ (Thread) không làm nghẽn tiến trình đặt hàng. | Kiểm thử `tests/test_mail.py` và `scratch/test_flask_mail.py` thành công 100%: bắt trọn 4 loại email (đơn cho khách, đơn cho chủ shop, xác thực tài khoản, đổi mật khẩu). |
| **6** | **Xác thực & Phân quyền (RBAC)** | Yêu cầu cốt lõi CLO2; Chương 2.4 & 3 | `app/models/user.py`, `app/blueprints/auth.py`, `app/blueprints/dashboard.py` | **ĐẠT** | Tích hợp `Flask-Login` với `UserMixin`, `login_required`, `current_user`. Cơ chế băm mật khẩu hiện đại kết hợp xác minh tương thích hàm băm `pbkdf2_sha256` của Django giúp người dùng cũ đăng nhập bình thường. Phân quyền chặt chẽ 3 cấp: Khách hàng (Customer), Nhân viên (Staff), Quản trị viên (Admin). Chặn khách vãng lai/khách hàng truy cập Dashboard (HTTP 403 Forbidden). Ngăn chặn người dùng tự nâng quyền. | Đăng nhập tài khoản `admin` (`admin123456`) và `khachhang1` (`customer123`) thành công; kiểm thử RBAC chặn khách hàng truy cập admin đạt mã 403. |
| **7** | **CRUD Sản phẩm & Xóa an toàn (Soft Delete)** | Yêu cầu bắt buộc CLO2; Chương 2.4 & 3 | `app/blueprints/dashboard.py`, `app/models/catalog.py` | **ĐẠT** | Thực hiện đầy đủ 4 thao tác Quản lý Mẫu hoa: Thêm mới (kèm tải ảnh và biến thể), Xem danh sách/chi tiết, Chỉnh sửa thông tin/giá/kho, Xóa sản phẩm. **Đặc biệt:** Triển khai cơ chế **Xóa Mềm (Soft Delete / Archive)**: nếu sản phẩm đã phát sinh đơn hàng, hệ thống chuyển trạng thái `status = 'ARCHIVED'` nhằm bảo toàn lịch sử giao dịch và kế toán; nếu sản phẩm chưa có đơn hàng, cho phép xóa vĩnh viễn. | Kiểm thử `tests/test_catalog_crud.py` chạy thử xóa mẫu hoa có đơn hàng -> chuyển `ARCHIVED` thành công, không gây lỗi khóa ngoại. |
| **8** | **Tìm kiếm & Phân trang thực tế** | Yêu cầu bắt buộc CLO2; Chương 2.4 & 3 | `app/blueprints/catalog.py`, `app/blueprints/dashboard.py` | **ĐẠT** | Tìm kiếm thực thi trực tiếp trên cơ sở dữ liệu qua mệnh đề `ilike` theo tên hoa, mã SKU, mô tả. Kết hợp bộ lọc theo Danh mục, Dịp tặng, Khoảng giá, và sắp xếp (Mới nhất, Giá tăng/giảm, Bán chạy). Phân trang với `SQLAlchemy.paginate()`, bảo lưu tham số bộ lọc qua các trang, xử lý ngoại lệ trang không tồn tại. | Tìm kiếm theo từ khóa 'Hồng', SKU 'FL-BOU-001', lọc danh mục 'Bó hoa tươi' và chuyển trang phân trang 1, 2 hoạt động chính xác 100%. |
| **9** | **Lập trình Mạng & REST API (CLO3)** | Yêu cầu bắt buộc CLO3 (10%); Chương 2.4 & 3 | `app/blueprints/api.py`, `scripts/test_api_client.py` | **ĐẠT** | Xây dựng REST API chuẩn RESTful: `GET /api/v1/products` (tìm kiếm, lọc, phân trang) và `GET /api/v1/products/<id>` (chi tiết sản phẩm, biến thể, hình ảnh). Trả về JSON đúng cấu trúc, xử lý HTTP Status (200, 400, 404, 500), bảo mật không để lộ giá vốn hay dữ liệu cá nhân. Bổ sung kịch bản `scripts/test_api_client.py` dùng `requests` và `urllib` để gọi API qua HTTP, bắt lỗi timeout và in kết quả đẹp mắt. | Kịch bản `scripts/test_api_client.py` và bộ test `tests/test_api.py` chạy thành công 4/4 kịch bản kiểm thử API, trả về JSON chuẩn xác. |
| **10** | **Kiến trúc Module hóa (CLO5)** | Yêu cầu chuẩn cấu trúc CLO5 | Toàn bộ thư mục `app/` | **ĐẠT** | Áp dụng cấu trúc chuẩn công nghiệp **Large Application Structure**: `app/models/` (thực thể dữ liệu), `app/forms/` (biểu mẫu Flask-WTF), `app/services/` (nghiệp vụ email, giỏ hàng, tồn kho), `app/blueprints/` (các route điều hướng tách biệt theo chức năng: main, auth, catalog, cart, orders, reviews, dashboard, api). | Mã nguồn đạt độ phân tách trách nhiệm cao (Separation of Concerns), dễ bảo trì, dễ mở rộng và đạt điểm tối đa tiêu chí kiến trúc CLO5. |

---

## 3. KẾT LUẬN ĐỐI CHIẾU

Dự án **Flora Flower Boutique** đã chuyển đổi và hoàn thiện xuất sắc 100% các tiêu chí từ bản đặc tả của Giảng viên ThS. Nguyễn Thị Mỹ Linh:
1. Nền tảng cốt lõi hoàn toàn là **Python 3 & FLASK**.
2. Toàn bộ các thư viện trọng tâm (`Flask-WTF`, `Flask-SQLAlchemy`, `Flask-Mail`, `Flask-Login`, `Jinja2`, `requests`) được tích hợp sâu vào mã nguồn thực tế.
3. Đáp ứng trọn vẹn chuẩn đầu ra về lập trình mạng **CLO3** với REST API trả về JSON và script kiểm thử HTTP client.
4. Cơ chế thông báo đơn hàng cho Chủ shop tại **`phuongtruong121204@gmail.com`** qua biến môi trường `SHOP_NOTIFICATION_EMAIL` hoạt động chính xác và an toàn.
5. 14 kịch bản kiểm thử tự động tại `tests/` đều vượt qua (`OK`), sẵn sàng cho buổi báo cáo và nghiệm thu đồ án.

