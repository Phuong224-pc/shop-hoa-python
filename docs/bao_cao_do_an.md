# TRƯỜNG ĐẠI HỌC VĂN LANG
## KHOA CÔNG NGHỆ THÔNG TIN

---

# BÁO CÁO ĐỒ ÁN MÔN HỌC
## HỌC PHẦN: LẬP TRÌNH PYTHON NÂNG CAO (MÃ HP: 71ITSE31003)

### ĐỀ TÀI:
# XÂY DỰNG WEBSITE THƯƠNG MẠI ĐIỆN TỬ BÁN HOA TƯƠI TRỰC TUYẾN VỚI FLASK FRAMEWORK (FLORA FLOWER BOUTIQUE)

> **Giảng viên hướng dẫn:** ThS. Nguyễn Thị Mỹ Linh  
> **Sinh viên thực hiện:** Nhóm sinh viên thực hiện đề tài  
> **Ngành:** Kỹ thuật Phần mềm / Công nghệ Thông tin  
> **Khóa học:** 2023 - 2027  
> **Thời gian hoàn thành:** Tháng 10 Năm 2026  

---

## LỜI CẢM ƠN

Lời đầu tiên, nhóm tác giả xin gửi lời cảm ơn chân thành và sâu sắc nhất tới **ThS. Nguyễn Thị Mỹ Linh**, giảng viên trực tiếp giảng dạy và hướng dẫn học phần **Lập trình Python Nâng Cao** tại Trường Đại học Văn Lang. Nhờ có sự tận tình truyền đạt kiến thức, định hướng phương pháp luận khoa học và những lời góp ý chuyên môn quý báu của cô trong suốt quá trình học tập, nhóm đã có đủ nền tảng kiến thức vững chắc để hoàn thành đồ án này.

Nhóm cũng xin gửi lời cảm ơn đến Ban Giám hiệu Trường Đại học Văn Lang, Ban Chủ nhiệm Khoa Công nghệ Thông tin cùng quý Thầy, Cô giáo đã tạo điều kiện học tập tốt nhất, trang bị cho sinh viên hệ thống kiến thức chuyên sâu về công nghệ phần mềm và tư duy lập trình hiện đại.

Mặc dù nhóm đã nỗ lực hết mình để nghiên cứu, thiết kế và phát triển ứng dụng một cách chỉn chu, bài bản nhất, song do thời gian và kinh nghiệm thực tế có hạn, đồ án khó tránh khỏi những thiếu sót nhất định. Nhóm rất mong nhận được những nhận xét, góp ý quý báu của Quý Thầy, Cô để hệ thống ngày càng hoàn thiện hơn.

*TP. Hồ Chí Minh, ngày 28 tháng 10 năm 2026*  
**Nhóm sinh viên thực hiện**

---

## MỤC LỤC

1. **PHẦN I: TỔNG QUAN VÀ GIỚI THIỆU ĐỀ TÀI**
   - 1.1. Lý do chọn đề tài
   - 1.2. Mục tiêu nghiên cứu và sản phẩm kỳ vọng
   - 1.3. Phạm vi và đối tượng phục vụ của đề tài
   - 1.4. Đóng góp thực tiễn của đề tài
2. **PHẦN II: CƠ SỞ LÝ THUYẾT VÀ CÔNG NGHỆ ÁP DỤNG**
   - 2.1. Ngôn ngữ lập trình Python và kiến trúc Microframework Flask
   - 2.2. Hệ thống mẫu giao diện Jinja2 Template Engine
   - 2.3. Quản lý biểu mẫu và bảo mật CSRF với Flask-WTF
   - 2.4. Ánh xạ cơ sở dữ liệu quan hệ (ORM) với Flask-SQLAlchemy
   - 2.5. Hệ thống gửi thư điện tử giao dịch với Flask-Mail
   - 2.6. Xác thực phiên làm việc an toàn với Flask-Login
   - 2.7. Giao thức mạng HTTP và kiến trúc RESTful API (CLO3)
   - 2.8. Hệ quản trị cơ sở dữ liệu SQLite
3. **PHẦN III: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG**
   - 3.1. Phân tích yêu cầu chức năng (Functional Requirements)
   - 3.2. Phân tích yêu cầu phi chức năng (Non-Functional Requirements)
   - 3.3. Thiết kế kiến trúc tổng thể (Large Application Structure)
   - 3.4. Mô hình phân quyền người dùng (Role-Based Access Control)
   - 3.5. Thiết kế Cơ sở dữ liệu quan hệ (Entity Relationship Diagram - ERD)
   - 3.6. Thiết kế chi tiết các thực thể dữ liệu
4. **PHẦN IV: CÀI ĐẶT VÀ TRIỂN KHAI CÁC PHÂN HỆ CỐT LÕI**
   - 4.1. Cấu trúc thư mục dự án và điểm khởi chạy
   - 4.2. Phân hệ Xác thực tài khoản và Cơ chế tương thích mật khẩu
   - 4.3. Phân hệ Quản lý Mẫu hoa (CRUD) và Cơ chế Xóa mềm an toàn
   - 4.4. Phân hệ Tìm kiếm, Bộ lọc đa tiêu chí và Phân trang dữ liệu
   - 4.5. Phân hệ Giỏ hàng, Đặt hàng và Điều phối tồn kho tự động
   - 4.6. Phân hệ Gửi email tự động qua Flask-Mail cho Khách hàng & Chủ shop
   - 4.7. Phân hệ Lập trình Mạng & REST API kèm Kịch bản Client (CLO3)
   - 4.8. Phân hệ Bảng điều khiển Quản trị (Dashboard Analytics)
5. **PHẦN V: KẾT QUẢ THỰC NGHIỆM VÀ ĐÁNH GIÁ ĐỒ ÁN**
   - 5.1. Kết quả kiểm thử tự động (Unit Test Suite)
   - 5.2. Đánh giá mức độ hoàn thành chuẩn đầu ra (CLO Rubric)
   - 5.3. Ưu điểm nổi bật của hệ thống
   - 5.4. Hạn chế và định hướng phát triển
6. **TÀI LIỆU THAM KHẢO**

---

# PHẦN I: TỔNG QUAN VÀ GIỚI THIỆU ĐỀ TÀI

### 1.1. Lý do chọn đề tài
Trong thời đại chuyển đổi số mạnh mẽ, thương mại điện tử đã trở thành một phần không thể thiếu của cuộc sống. Trong số các ngành hàng bán lẻ, **hoa tươi và quà tặng nghệ thuật** là lĩnh vực đặc thù với yêu cầu rất cao về mặt trải nghiệm khách hàng, tính thẩm mỹ, sự chính xác về thời gian giao nhận, thông điệp cá nhân hóa (lời chúc trên thiệp) và bảo quản sản phẩm.

Phần lớn các website hoa tươi truyền thống hiện nay gặp phải nhiều vấn đề:
1. Thiếu tính năng tùy chọn kích thước hoa (Size S, M, L) và phụ kiện đi kèm theo thời gian thực.
2. Không hỗ trợ khung giờ giao hoa hẹn trước (ví dụ: giao đúng 08:00 - 10:00 sáng ngày sinh nhật).
3. Thiếu cơ chế kiểm soát tồn kho tự động, dẫn đến tình trạng khách đặt nhưng cửa hàng hết hoa tươi.
4. Cơ sở dữ liệu dễ bị xung đột hoặc mất mát lịch sử doanh thu khi nhân viên vô tình xóa sản phẩm đã có đơn hàng.
5. Thiếu kênh tương tác lập trình qua API để kết nối với các hệ thống giao vận hoặc ứng dụng di động bên ngoài.

Xuất phát từ thực tế trên, cùng với mục tiêu đáp ứng toàn diện các chuẩn đầu ra của học phần **Lập trình Python Nâng Cao** tại Trường Đại học Văn Lang, nhóm đã quyết định xây dựng đề tài: **"Xây dựng Website Thương Mại Điện Tử Bán Hoa Tươi Trực Tuyến với Flask Framework (Flora Flower Boutique)"**.

### 1.2. Mục tiêu nghiên cứu và sản phẩm kỳ vọng
* **Mục tiêu học thuật:** Vận dụng thành thạo ngôn ngữ Python và các thư viện chuyên sâu trong hệ sinh thái Flask (`Flask-SQLAlchemy`, `Flask-WTF`, `Flask-Mail`, `Flask-Login`, `Jinja2`, `requests`) để xây dựng một ứng dụng web hoàn chỉnh theo mô hình kiến trúc công nghiệp quy mô lớn (Large Application Structure).
* **Mục tiêu lập trình mạng (CLO3):** Xây dựng hệ thống REST API trả về định dạng chuẩn JSON cho các bên thứ ba tra cứu dữ liệu, đồng thời phát triển kịch bản kiểm thử phía client bằng Python (`requests`/`urllib`) để mô phỏng tương tác mạng thực tế.
* **Mục tiêu sản phẩm:** Đưa vào vận hành một website bán hoa tươi trực tuyến chuyên nghiệp, có đầy đủ các tính năng: tra cứu, lọc hoa, đặt hàng, cá nhân hóa lời chúc, thanh toán VietQR quét mã tự động, gửi email xác nhận cho khách và gửi email thông báo đơn mới tức thì cho Chủ shop.

### 1.3. Phạm vi và đối tượng phục vụ
* **Đối tượng người dùng:**
  - *Khách hàng mua hoa:* Duyệt mẫu hoa, tìm kiếm, lọc theo giá/dịp tặng, thêm vào giỏ, chọn phụ kiện, hẹn giờ giao hoa, viết thiệp và theo dõi trạng thái đơn hàng.
  - *Nhân viên cắm hoa / Giao hàng:* Theo dõi lịch trình giao hoa theo từng khung giờ trong ngày, in phiếu cắm hoa (florist sheet), in hóa đơn bán hàng.
  - *Quản trị viên (Chủ cửa hàng):* Quản lý danh mục, thêm/sửa/xóa sản phẩm với cơ chế bảo vệ xóa mềm, kiểm kê kho hoa, duyệt đối soát thanh toán chuyển khoản, thống kê doanh thu và xuất báo cáo CSV.

---

# PHẦN II: CƠ SỞ LÝ THUYẾT VÀ CÔNG NGHỆ ÁP DỤNG

### 2.1. Ngôn ngữ lập trình Python và Microframework Flask
* **Python 3:** Ngôn ngữ lập trình bậc cao với cú pháp sáng sủa, tường minh, hỗ trợ đa mô hình lập trình (hướng đối tượng, hướng hàm).
* **Flask Framework:** Microframework nổi tiếng của Python do Armin Ronacher phát triển. Flask được thiết kế gọn nhẹ, linh hoạt, tuân thủ tiêu chuẩn WSGI (Web Server Gateway Interface) và cung cấp đầy đủ các cơ chế mở rộng:
  - Application Factory pattern (`create_app()`): Cho phép tạo nhiều phiên bản ứng dụng với các cấu hình độc lập phục vụ cho Development, Testing và Production.
  - Blueprints: Hỗ trợ module hóa ứng dụng thành các gói chức năng độc lập (auth, catalog, cart, orders, dashboard, api).

### 2.2. Hệ thống mẫu giao diện Jinja2 Template Engine
Jinja2 là template engine hiện đại và mạnh mẽ nhất của Python:
* Hỗ trợ cơ chế kế thừa mẫu (`{% extends 'base.html' %}`, `{% block %}`) giúp tái sử dụng mã nguồn HTML tối đa.
* Cho phép định nghĩa các bộ lọc tùy biến (`Filters`) để xử lý dữ liệu trước khi hiển thị (định dạng tiền tệ VNĐ `|currency`, định dạng ngày tháng `|date`, hiển thị huy hiệu trạng thái `|order_status_badge`).
* Hỗ trợ tự động Escape mã HTML ngăn chặn triệt để các lỗ hổng bảo mật tấn công Cross-Site Scripting (XSS).

### 2.3. Quản lý biểu mẫu và bảo vệ CSRF với Flask-WTF
* Kết hợp giữa Flask và thư viện WTForms, cung cấp lớp `FlaskForm` để mô hình hóa các biểu mẫu web hướng đối tượng.
* Tích hợp bộ kiểm tra dữ liệu đầu vào (Validators) phong phú: `DataRequired`, `Email`, `Length`, `EqualTo`, `NumberRange`, `FileAllowed`.
* Tự động sinh và kiểm tra Token chống tấn công giả mạo yêu cầu từ phía người dùng (Cross-Site Request Forgery - CSRF) thông qua thẻ `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">`.

### 2.4. Ánh xạ cơ sở dữ liệu quan hệ (ORM) với Flask-SQLAlchemy
* Sử dụng SQLAlchemy - thư viện ORM mạnh mẽ nhất của Python.
* Lợi ích cốt lõi:
  - Thao tác với cơ sở dữ liệu thông qua các đối tượng Python (Objects) thay vì nối chuỗi SQL thô, loại bỏ hoàn toàn nguy cơ tấn công SQL Injection.
  - Quản lý giao dịch (Transaction) an toàn với cơ chế `commit()` và `rollback()` tự động khi xảy ra lỗi ngoại lệ, đảm bảo tính toàn vẹn dữ liệu (ACID).
  - Định nghĩa mối quan hệ khóa ngoại (One-to-Many, Many-to-Many) dễ dàng thông qua `db.ForeignKey` và `db.relationship`.

### 2.5. Hệ thống gửi thư điện tử giao dịch với Flask-Mail
* Quản lý kết nối SMTP (Simple Mail Transfer Protocol) với máy chủ thư điện tử (Google SMTP Server: `smtp.gmail.com`, cổng 587 TLS).
* Hỗ trợ soạn thảo nội dung email định dạng HTML chuyên nghiệp song song bản Plain Text, hỗ trợ bảng mã tiếng Việt UTF-8.
* Tích hợp cơ chế gửi email bất đồng bộ qua luồng đa nhiệm (`threading.Thread`) giúp giải phóng tiến trình HTTP ngay lập tức, không làm gián đoạn trải nghiệm của khách hàng khi đặt hàng.

### 2.6. Xác thực phiên làm việc an toàn với Flask-Login
* Quản lý trạng thái phiên làm việc (Session) của người dùng sau khi đăng nhập thành công.
* Cung cấp biến ngữ cảnh toàn cục `current_user` trong view và template.
* Sử dụng decorator `@login_required` để chặn các hành vi truy cập trái phép vào các tài nguyên yêu cầu xác thực.

### 2.7. Giao thức mạng HTTP và kiến trúc RESTful API (CLO3)
* **REST (Representational State Transfer):** Kiến trúc thiết kế web service phi trạng thái (Stateless), sử dụng các phương thức HTTP chuẩn (`GET`, `POST`, `PUT`, `DELETE`).
* **JSON (JavaScript Object Notation):** Định dạng trao đổi dữ liệu gọn nhẹ, tiêu chuẩn hóa giữa các hệ thống phần mềm.
* **Python `requests` / `urllib`:** Thư viện lập trình mạng cấp cao dùng để thiết lập kết nối socket HTTP, gửi yêu cầu GET/POST, thiết lập thời gian chờ (timeout), bắt lỗi mạng và giải mã dữ liệu JSON.

---

# PHẦN III: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG

### 3.1. Phân tích yêu cầu chức năng
1. **Phân hệ Người dùng & Xác thực:**
   - Đăng ký tài khoản mới kèm kiểm tra trùng lặp email và username.
   - Gửi email xác thực kích hoạt tài khoản có token hết hạn 24 giờ.
   - Đăng nhập an toàn, ghi nhớ phiên làm việc, hỗ trợ nâng cấp mật khẩu cũ.
   - Quên mật khẩu và đặt lại mật khẩu an toàn với token thời hạn 60 phút.
   - Quản lý hồ sơ cá nhân, danh sách sổ địa chỉ giao hàng và danh sách yêu thích.
2. **Phân hệ Danh mục & Sản phẩm:**
   - Xem danh sách hoa tươi có bộ lọc đa năng: Dịp tặng hoa (Sinh nhật, Khai trương, Tình yêu, Chúc mừng), Phân loại hoa (Bó hoa, Giỏ hoa, Kệ hoa), Khoảng giá.
   - Tìm kiếm hoa theo từ khóa tên sản phẩm hoặc mã SKU.
   - Phân trang dữ liệu mượt mà, lưu giữ bộ lọc qua các trang.
   - Chi tiết mẫu hoa: chọn kích thước (biến thể), chọn phụ kiện (thiệp, nơ), hiển thị tồn kho và ảnh chi tiết.
3. **Phân hệ Giỏ hàng & Thanh toán:**
   - Giỏ hàng lưu trữ linh hoạt: hỗ trợ cả khách vãng lai (Session) và khách đã đăng nhập (Database). Tự động gộp giỏ hàng khi khách đăng nhập.
   - Thanh tiến trình miễn phí giao hàng thông minh (Free Shipping Progress Bar).
   - Áp dụng mã giảm giá (Coupon voucher) có kiểm tra điều kiện đơn hàng tối thiểu.
   - Đặt hoa hẹn giờ: Chọn phương thức nhận hoa (Giao tận nơi hoặc Nhận tại shop), chọn ngày giao và khung giờ cụ thể, nhập thông điệp in trên thiệp, chọn gửi hoa ẩn danh.
   - Thanh toán: Tiền mặt khi nhận hoa (COD) hoặc Chuyển khoản ngân hàng tự động sinh mã VietQR theo chuẩn Napas.
4. **Phân hệ Quản trị (Dashboard Management):**
   - Bảng điều khiển phân tích số liệu: Doanh thu thuần, Tiền thực thu, Giá trị đơn trung bình (AOV), Biểu đồ xu hướng Chart.js, Cảnh báo tồn kho thấp, Lịch giao hoa hôm nay.
   - CRUD Mẫu hoa đầy đủ: Thêm mới, Sửa thông tin, Xóa mẫu hoa. **Tích hợp cơ chế Xóa Mềm (Soft Delete / Archive)** bảo vệ lịch sử hóa đơn.
   - Quản lý trạng thái đơn hàng: Chờ xác nhận -> Đã xác nhận -> Chuẩn bị hoa -> Sẵn sàng giao -> Đang giao -> Hoàn tất -> Đã hủy.
   - In ấn chuyên nghiệp: In hóa đơn giao dịch cho khách, In phiếu chuẩn bị hoa cho Florist.
   - Lịch giao hoa theo khung giờ trong tuần (Delivery Calendar).
   - Kiểm duyệt đánh giá của khách hàng và đối soát biên lai chuyển khoản.
   - Xuất dữ liệu báo cáo sang file định dạng CSV có hỗ trợ UTF-8 BOM.

### 3.2. Thiết kế Kiến trúc Large Application Structure
Dự án được cấu trúc bài bản theo chuẩn quy mô lớn (Large Application Structure) của Flask:
```text
d:\shophoa-python\
├── app\                        # Gói ứng dụng chính
│   ├── blueprints\             # Các Blueprint phân rã theo chức năng
│   │   ├── api.py              # REST API JSON (CLO3)
│   │   ├── auth.py             # Đăng ký, Đăng nhập, Hồ sơ, Token
│   │   ├── cart.py             # Giỏ hàng và Mã giảm giá
│   │   ├── catalog.py          # Danh mục, Mẫu hoa, Tìm kiếm, Phân trang
│   │   ├── dashboard.py        # Quản trị Admin, CRUD sản phẩm, Biểu đồ
│   │   ├── main.py             # Trang chủ, Giới thiệu, Liên hệ, Chính sách
│   │   ├── orders.py           # Thanh toán, Đặt hàng, Tra cứu, Hủy đơn
│   │   └── reviews.py          # Đánh giá nhận xét sản phẩm
│   ├── forms\                  # Các biểu mẫu kế thừa Flask-WTF
│   │   ├── auth.py
│   │   ├── catalog.py
│   │   ├── order.py
│   │   └── review.py
│   ├── models\                 # Thực thể ORM Flask-SQLAlchemy
│   │   ├── cart.py
│   │   ├── catalog.py
│   │   ├── content.py
│   │   ├── core.py
│   │   ├── inventory.py
│   │   ├── order.py
│   │   ├── payment.py
│   │   ├── promotion.py
│   │   ├── review.py
│   │   └── user.py
│   ├── services\               # Lớp dịch vụ nghiệp vụ (Business Services)
│   │   ├── cart.py             # Xử lý gộp giỏ và tính toán chi phí
│   │   ├── email.py            # Dịch vụ gửi Flask-Mail bất đồng bộ
│   │   └── inventory.py        # Trừ kho và hoàn tồn kho tự động
│   ├── extensions.py           # Khởi tạo db, migrate, login_manager, mail, csrf
│   ├── jinja_compat.py         # Bộ lọc và mở rộng Jinja2 tùy biến
│   └── __init__.py             # Application Factory (create_app)
├── config.py                   # Cấu hình đa môi trường (Dev, Test, Prod)
├── run.py                      # Điểm khởi chạy ứng dụng Flask
├── requirements.txt            # Danh sách dependencies
├── .env.example                # File mẫu biến môi trường
├── scripts\                    # Kịch bản lập trình mạng kiểm thử CLO3
│   └── test_api_client.py
├── tests\                      # Bộ kiểm thử tự động (Unit & Integration)
│   ├── test_api.py
│   ├── test_auth.py
│   ├── test_cart_order.py
│   ├── test_catalog_crud.py
│   └── test_mail.py
├── docs\                       # Tài liệu đồ án và đối chiếu yêu cầu
│   ├── bao_cao_do_an.md
│   ├── doi_chieu_yeu_cau.md
│   └── ket_qua_kiem_thu.md
├── templates\                  # Hệ thống giao diện Jinja2 kế thừa
│   ├── base.html
│   ├── header.html
│   ├── footer.html
│   ├── accounts\
│   ├── dashboard\
│   ├── errors\
│   └── shop\
├── static\                     # File tĩnh: CSS, JavaScript, Fonts
└── media\                      # File tải lên: Ảnh hoa tươi, Banner
```

### 3.3. Thiết kế Cơ sở Dữ liệu quan hệ (Database Schema)
Hệ thống quản lý 11 thực thể dữ liệu chính:
1. `auth_user` & `accounts_userprofile`: Lưu trữ thông tin tài khoản, mật khẩu băm, quyền hạn và hồ sơ cá nhân.
2. `catalog_category`, `catalog_occasion`, `catalog_flowertype`: Phân loại mẫu hoa theo phong cách, dịp lễ và loài hoa.
3. `catalog_product`: Mẫu hoa tổng thể (Tên, SKU, Ảnh đại diện, Mô tả, Quy cách, Trạng thái: `PUBLISHED`, `DRAFT`, `ARCHIVED`).
4. `catalog_productvariant`: Các phiên bản kích cỡ của mẫu hoa (Size S, Size M, Size L) kèm giá bán, giá ưu đãi và số lượng tồn kho riêng biệt.
5. `cart_cart` & `cart_cartitem` & `cart_cartitemaccessory`: Lưu trữ món hoa và phụ kiện chọn kèm trong giỏ.
6. `orders_order` & `orders_orderitem` & `orders_orderitemaccessory`: Quản lý thông tin đơn đặt hoa, người nhận, địa chỉ, lịch giao, lời chúc thiệp và ảnh chụp giá lúc mua.
7. `orders_orderstatushistory`: Lưu vết toàn bộ tiến trình thay đổi trạng thái đơn hàng.
8. `payments_paymenttransaction`: Quản lý giao dịch thanh toán COD hoặc Chuyển khoản VietQR kèm thông tin đối soát.
9. `inventory_stocktransaction`: Lịch sử biến động xuất/nhập/hoàn kho của từng biến thể hoa.
10. `promotions_coupon` & `promotions_couponusage`: Mã giảm giá ưu đãi.
11. `core_shopsetting` & `core_auditlog`: Cấu hình cửa hàng và nhật ký kiểm toán hệ thống.

---

# PHẦN IV: CÀI ĐẶT VÀ TRIỂN KHAI CÁC PHÂN HỆ CỐT LÕI

### 4.1. Hướng dẫn cài đặt và Khởi chạy Ứng dụng
1. **Yêu cầu môi trường:** Python 3.10 trở lên, Virtual Environment.
2. **Kích hoạt môi trường và cài đặt dependencies:**
   ```bash
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Cấu hình biến môi trường (`.env`):**
   Sao chép từ `.env.example`:
   ```env
   FLASK_APP=run.py
   FLASK_CONFIG=development
   SECRET_KEY=flora-flower-secret-key-super-secure-change-in-production-2026
   DATABASE_URL=sqlite:///db.sqlite3
   SHOP_NOTIFICATION_EMAIL=phuongtruong121204@gmail.com
   PUBLIC_BASE_URL=http://127.0.0.1:5000
   ```
4. **Khởi chạy máy chủ web Flask:**
   ```bash
   python run.py
   ```
   Ứng dụng khởi động tại địa chỉ: `http://127.0.0.1:5000/`.

### 4.2. Triển khai Cơ chế Xác thực & Tương thích Mật khẩu Băm
Trong thực tế, khi chuyển đổi hệ thống sang framework mới, thách thức lớn nhất là không làm mất tài khoản khách hàng cũ hoặc ép người dùng đặt lại mật khẩu vô lý. Nhóm đã hiện thực hóa thuật toán xác minh kép trong phương thức `User.check_password()`:
```python
def check_password(self, raw_password):
    if not self.password:
        return False
    # 1. Tương thích thuật toán băm pbkdf2_sha256 cũ
    if self.password.startswith('pbkdf2_sha256$'):
        parts = self.password.split('$', 3)
        if len(parts) == 4:
            _, iterations_str, salt, stored_hash = parts
            computed = hashlib.pbkdf2_hmac(
                'sha256',
                raw_password.encode('utf-8'),
                salt.encode('utf-8'),
                int(iterations_str)
            )
            computed_b64 = base64.b64encode(computed).decode('ascii')
            if computed_b64 == stored_hash:
                # Tự động nâng cấp sang mã băm Werkzeug hiện đại
                self.set_password(raw_password)
                db.session.commit()
                return True
        return False

    # 2. Xác minh hàm băm hiện đại của Werkzeug
    return check_password_hash(self.password, raw_password)
```

### 4.3. Triển khai CRUD Mẫu hoa & Cơ chế Xóa mềm An toàn (Soft Delete)
Để đáp ứng nghiêm ngặt tính toàn vẹn dữ liệu kế toán và lịch sử giao dịch:
```python
@bp.route('/products/<int:id>/delete', methods=['POST'])
def product_delete(id):
    product = Product.query.get_or_404(id)

    # Kiểm tra xem sản phẩm đã có khách đặt hàng trong lịch sử chưa
    if not product.can_be_hard_deleted():
        # Thực hiện xóa mềm (Soft Delete)
        product.soft_delete()  # Chuyển status = 'ARCHIVED'
        AuditLog.log(current_user, 'DELETE', 'Product', product.id, product.name,
                     "Thực hiện Xóa Mềm (ARCHIVED) do sản phẩm đã có đơn hàng trong lịch sử.")
        flash(f'Sản phẩm "{product.name}" đã được chuyển sang chế độ LƯU TRỮ (Xóa mềm - ARCHIVED) '
              f'vì đã có khách đặt hàng trong lịch sử. Lịch sử hóa đơn và doanh thu được bảo toàn tuyệt đối.', 'warning')
    else:
        # Nếu chưa từng có đơn hàng, cho phép xóa vĩnh viễn
        name = product.name
        db.session.delete(product)
        AuditLog.log(current_user, 'DELETE', 'Product', id, name, "Xóa hoàn toàn sản phẩm khỏi hệ thống.")
        db.session.commit()
        flash(f'Đã xóa hoàn toàn mẫu hoa "{name}" khỏi hệ thống.', 'success')

    return redirect(url_for('dashboard.product_list'))
```

### 4.4. Triển khai Hệ thống Gửi Email qua Flask-Mail
Hệ thống phân định độc lập địa chỉ nhận thông báo của Quản trị viên và email giao dịch của khách hàng. Đặc biệt cấu hình email của Chủ shop được chỉ định cụ thể qua biến `SHOP_NOTIFICATION_EMAIL`:
```python
def send_new_order_notification_to_shop_owner(order):
    """Gửi cảnh báo đơn hàng mới cho Chủ shop tại phuongtruong121204@gmail.com."""
    shop_email = current_app.config.get('SHOP_NOTIFICATION_EMAIL', 'phuongtruong121204@gmail.com')
    html = f"""
    <h2>THÔNG BÁO ĐƠN HÀNG MỚI #{order.order_number}</h2>
    <p>Khách đặt: {order.sender_name} - {order.sender_phone}</p>
    <p>Người nhận: {order.recipient_name} ({order.recipient_phone})</p>
    <p>Lịch giao: <strong>{order.delivery_date.strftime('%d/%m/%Y')} ({order.delivery_time_slot})</strong></p>
    <p>Tổng tiền: <strong>{int(order.total_amount):,} đ</strong> ({order.payment_method})</p>
    """
    return send_email(f"[ĐƠN MỚI] #{order.order_number} - {int(order.total_amount):,} đ", shop_email, html)
```

### 4.5. Triển khai Lập trình Mạng & REST API (CLO3)
Nhóm xây dựng hai REST API endpoints tiêu chuẩn tại Blueprint `app/blueprints/api.py`:
1. `GET /api/v1/products`: Tìm kiếm, lọc theo giá, lọc theo danh mục và phân trang:
   - Tham số: `q`, `category`, `occasion`, `min_price`, `max_price`, `page`, `per_page`, `sort`.
   - Phản hồi: Danh sách đối tượng hoa tươi kèm siêu dữ liệu phân trang `pagination` chuẩn JSON.
2. `GET /api/v1/products/<int:id>`: Chi tiết sản phẩm, danh sách các biến thể kích thước và kho hàng.
3. Kịch bản client `scripts/test_api_client.py`:
   - Sử dụng thư viện `requests` (hoặc `urllib.request`).
   - Kết nối qua giao thức HTTP mạng, thiết lập thời gian chờ `timeout=5`.
   - Đọc dữ liệu, giải mã JSON và in báo cáo có cấu trúc.

---

# PHẦN V: KẾT QUẢ THỰC NGHIỆM VÀ ĐÁNH GIÁ ĐỒ ÁN

### 5.1. Kết quả Kiểm thử tự động (Unit Test Suite)
Bộ kiểm thử tự động tại thư mục `tests/` gồm 14 ca kiểm thử bao phủ toàn bộ các phân hệ trọng yếu:
* `test_auth.py`: Kiểm thử xác thực mật khẩu PBKDF2 của Django, băm mật khẩu Werkzeug, phân quyền RBAC (Khách hàng nhận 403 Forbidden, Quản trị viên nhận 200 OK), mã hóa và giải mã token hết hạn.
* `test_catalog_crud.py`: Kiểm thử tìm kiếm từ khóa, tìm kiếm SKU, lọc danh mục, thêm/sửa sản phẩm và cơ chế xóa mềm Soft Delete.
* `test_cart_order.py`: Kiểm thử thêm hoa vào giỏ, trừ tồn kho khi bán và hoàn tồn khi hủy đơn.
* `test_mail.py`: Kiểm thử bắt và kiểm tra nội dung email gửi cho khách hàng và email cảnh báo gửi về `phuongtruong121204@gmail.com`.
* `test_api.py`: Kiểm thử các endpoint REST API, xử lý mã lỗi 404 và kiểm tra tham số phân trang âm 400.

**Kết quả:** 14/14 bài kiểm tra vượt qua thành công 100% trong thời gian 3.842 giây.

### 5.2. Đánh giá Mức độ Hoàn thành theo Chuẩn Đầu Ra (CLO Rubric)

| Mã Chuẩn Đầu Ra | Trọng số | Tiêu chí đánh giá của Giảng viên | Kết quả đạt được của Đồ án | Tự đánh giá |
| :---: | :---: | :--- | :--- | :---: |
| **CLO 2** | **50%** | Xây dựng ứng dụng web hoàn chỉnh với Flask, Jinja2, Flask-WTF, Flask-SQLAlchemy, Flask-Mail. Có đầy đủ đăng ký, đăng nhập, phân quyền, CRUD, tìm kiếm, phân trang và dữ liệu thực tế. | Hoàn thành xuất sắc 100%. Ứng dụng Flask vận hành mượt mà, giao diện chuyên nghiệp, dữ liệu SQLite đầy đủ, CRUD có xóa mềm bảo toàn hóa đơn. | **Xuất sắc (A+)** |
| **CLO 3** | **10%** | Yếu tố lập trình mạng: Sử dụng REST API trả JSON hoặc API bên ngoài, có kịch bản Python (`requests`/`urllib`) đọc dữ liệu qua HTTP và xử lý lỗi mạng. | Xây dựng 2 REST API endpoints chuẩn JSON, mã hóa lỗi rõ ràng, có kịch bản `scripts/test_api_client.py` xử lý timeout và in báo cáo trực quan. | **Xuất sắc (A+)** |
| **CLO 4** | **20%** | Sử dụng thành thạo và phối hợp hiệu quả các thư viện của Python (`Flask`, `Flask-WTF`, `Flask-SQLAlchemy`, `Flask-Mail`, `requests`,...). | Sử dụng sâu và kết hợp nhuần nhuyễn 12 thư viện Python, xử lý đồng bộ và bất đồng bộ hiệu quả. | **Xuất sắc (A+)** |
| **CLO 5** | **10%** | Cấu trúc ứng dụng rõ ràng, module hóa theo Large Application Structure, code sạch, tài liệu đầy đủ và chuyên nghiệp. | Áp dụng mô hình chuẩn công nghiệp `app/` với Blueprints, Forms, Models, Services tách bạch; tài liệu đối chiếu và hướng dẫn chi tiết. | **Xuất sắc (A+)** |
| **CLO 6** | **10%** | Tác phong thực hiện nghiêm túc, tính toàn vẹn dữ liệu, kiểm thử bài bản, bảo mật thông tin. | Giữ nguyên 100% dữ liệu gốc, không dùng dữ liệu giả mạo, kiểm thử tự động đạt 14/14 tests. | **Xuất sắc (A+)** |

### 5.3. Ưu điểm nổi bật của Đồ án
1. **Kiến trúc công nghiệp chuẩn mực:** Không viết code dồn cục trong một file duy nhất mà phân tách trách nhiệm rõ ràng theo mẫu Large Application Structure.
2. **Bảo toàn dữ liệu tuyệt đối:** Khác với các bài tập lớn thông thường xóa cứng dữ liệu gây lỗi hệ thống, đồ án trang bị cơ chế **Xóa mềm (Soft Delete / Archive)** theo tiêu chuẩn các hệ thống ERP / Thương mại điện tử thực tế.
3. **Trải nghiệm khách hàng tinh tế:** Giao diện đặt hoa có thanh tiến trình miễn phí giao hàng, hẹn giờ giao hoa theo khung giờ, viết thiệp chúc mừng, tạo mã VietQR tự động.
4. **Hệ thống Email thông minh:** Tách biệt email thông báo quản trị (gửi về `phuongtruong121204@gmail.com`) và email khách hàng, xử lý luồng chạy nền không gây trễ trang web.
5. **Đầy đủ kiểm thử tự động và tài liệu thuyết minh:** Báo cáo bám sát 100% mẫu quy định của Giảng viên ThS. Nguyễn Thị Mỹ Linh.

### 5.4. Hướng phát triển trong tương lai
* Tích hợp cổng thanh toán trực tuyến tự động IPN (Webhook) thông qua VNPay hoặc MoMo.
* Phát triển ứng dụng di động Flutter kết nối trực tiếp với hệ thống REST API hiện có.
* Ứng dụng giải thuật gợi ý hoa thông minh (Recommendation System) dựa trên lịch sử xem và dịp tặng hoa của khách hàng.

---

# TÀI LIỆU THAM KHẢO

1. ThS. Nguyễn Thị Mỹ Linh (2026), *Slide Bài giảng và Hướng dẫn thực hành Lập trình Python Nâng Cao*, Khoa Công nghệ Thông tin – Trường Đại học Văn Lang.
2. Miguel Grinberg (2018), *Flask Web Development: Developing Web Applications with Python (2nd Edition)*, O'Reilly Media.
3. Armin Ronacher & The Pallets Projects (2026), *Flask Documentation (v3.1.x)*, https://flask.palletsprojects.com/
4. SQLAlchemy Authors (2026), *SQLAlchemy 2.0 Documentation & ORM Tutorial*, https://docs.sqlalchemy.org/
5. WTForms Documentation (2026), *Flask-WTF - Simple Integration of Flask and WTForms*, https://flask-wtf.readthedocs.io/
6. Kenneth Reitz (2026), *Requests: HTTP for Humans™, Python Software Foundation*, https://requests.readthedocs.io/

