# 🌸 FLORA FLOWER - WEBSITE THƯƠNG MẠI ĐIỆN TỬ HOA TƯƠI & QUẢN TRỊ NGHIỆP VỤ BÁN HOA

> **ĐỒ ÁN HỌC PHẦN: LẬP TRÌNH PYTHON NÂNG CAO**  
> **Mã học phần:** 71ITSE31003 | **Khoa Công Nghệ Thông Tin – Đại học Văn Lang**  
> **Giảng viên hướng dẫn:** ThS. Nguyễn Thị Mỹ Linh  
> **Nền tảng công nghệ:** Python 3.12+ | Flask 3.x (Large Application Structure)

---

## 📌 1. Giới Thiệu Tổng Quan Đề Tài

**FLORA FLOWER BOUTIQUE** là website thương mại điện tử chuyên sâu cho ngành hoa tươi và quà tặng nghệ thuật. Ứng dụng được thiết kế và xây dựng hoàn chỉnh bằng **Python & Flask**, đáp ứng 100% các tiêu chuẩn đánh giá theo Rubric học phần:
- **CLO2 (50%):** Thiết kế và xây dựng web Flask hoàn chỉnh: Application Factory, Blueprints, Jinja2 template inheritance, Web Forms (Flask-WTF + CSRF protection), Database (Flask-SQLAlchemy ORM + SQLite), Email giao dịch tự động (Flask-Mail).
- **CLO3 (10%):** Lập trình mạng & tích hợp API: Xây dựng hệ thống REST API chuẩn JSON (`/api/v1/...`) và script client tự động gọi HTTP (`requests` / `urllib`).
- **CLO4 (20%):** Sử dụng thành thạo hệ sinh thái thư viện Python: Flask, Flask-WTF, WTForms, Flask-SQLAlchemy, Flask-Login, Flask-Mail, requests, python-dotenv, Pillow.
- **CLO5 (10%):** Module hóa mã nguồn theo mô hình Large Application Structure rõ ràng, sạch sẽ, dễ bảo trì.
- **CLO6 (10%):** Đầy đủ bộ test tự động (14 unit/integration tests), kịch bản demo và tài liệu báo cáo chuẩn mẫu.

---

## 🛠️ 2. Công Nghệ Sử Dụng (Tech Stack)

- **Ngôn ngữ:** Python 3.12+ / 3.14+
- **Web Framework:** Flask 3.x (Kiến trúc Application Factory `create_app` & 8 Blueprints độc lập)
- **Cơ sở dữ liệu (ORM):** Flask-SQLAlchemy (SQLAlchemy 2.x) kết hợp SQLite (`db.sqlite3`)
- **Quản lý Form & Bảo mật:** Flask-WTF + WTForms + CSRF Protection + Password Hashing (PBKDF2 / Werkzeug)
- **Xác thực & Phân quyền:** Flask-Login + Role-Based Access Control (`ADMIN`, `STAFF`, `CUSTOMER`)
- **Dịch vụ Email:** Flask-Mail (SMTP Gmail TLS 587) gửi xác nhận đơn hàng, gửi cảnh báo tức thì về email chủ shop (`phuongtruong121204@gmail.com`)
- **Lập trình mạng (CLO3):** REST API JSON (`/api/v1/products`) + HTTP client `scripts/test_api_client.py`
- **Giao diện người dùng:** Jinja2 Templates + Bootstrap 5.3 + Bootstrap Icons + Chart.js + Vanilla JS

---

## 📂 3. Cấu Trúc Thư Mục Dự Án (Large Application Structure)

```text
d:\shophoa-python/
├── app/                             # Gói ứng dụng Flask trung tâm
│   ├── blueprints/                  # 8 Blueprint phân tầng nghiệp vụ
│   │   ├── api.py                   # REST API trả về JSON (CLO3)
│   │   ├── auth.py                  # Đăng ký, đăng nhập, hồ sơ cá nhân, đổi/quên mật khẩu
│   │   ├── cart.py                  # Thao tác giỏ hàng, cập nhật số lượng, áp dụng mã ưu đãi
│   │   ├── catalog.py               # Danh mục hoa, dịp tặng, chi tiết hoa, tìm kiếm, lọc
│   │   ├── dashboard.py             # Cổng quản trị: hoa, kho, đơn hàng, duyệt thanh toán, khách hàng
│   │   ├── main.py                  # Trang chủ, giới thiệu, liên hệ, câu hỏi thường gặp FAQ
│   │   ├── orders.py                # Đặt hàng checkout, upload biên lai VietQR, tra cứu đơn
│   │   └── reviews.py               # Viết và duyệt đánh giá chất lượng hoa
│   ├── forms/                       # Các lớp FlaskForm xác thực dữ liệu & chống CSRF
│   ├── models/                      # 14 Models SQLAlchemy ORM quản lý quan hệ thực thể
│   ├── services/                    # Tầng nghiệp vụ xử lý email, kho, giỏ hàng
│   ├── extensions.py                # Khởi tạo db, migrate, login_manager, mail, csrf
│   ├── jinja_compat.py              # Bộ lọc template, định dạng tiền tệ VNĐ, badge trạng thái
│   └── __init__.py                  # Application Factory create_app()
├── docs/                            # Hồ sơ báo cáo & kịch bản bảo vệ đồ án
│   ├── Mau_Bao_Cao_DoAn_LapTrinhPythonNangCao.docx # File mẫu báo cáo của Giảng viên
│   ├── bao_cao_do_an.md             # Báo cáo đồ án chi tiết 5 chương
│   ├── database_schema.md           # Thiết kế cơ sở dữ liệu ERD
│   ├── endpoints.md                 # Danh mục toàn bộ URL endpoint
│   └── presentation_script.md       # Kịch bản thuyết trình bảo vệ 15 phút
├── media/                           # Hình ảnh hoa tươi, danh mục, banner và biên lai chuyển khoản
├── static/                          # File tĩnh CSS (theme Boutique), JavaScript, biểu đồ
├── templates/                       # Giao diện Jinja2 kế thừa từ base.html
│   ├── shop/                        # Giao diện khách hàng mua hoa (Trang chủ, chi tiết, checkout...)
│   ├── dashboard/                   # Giao diện quản trị Admin/Staff (Sản phẩm, đơn hàng, kho, doanh thu...)
│   ├── accounts/                    # Giao diện xác thực (Đăng nhập, đăng ký, hồ sơ)
│   └── errors/                      # Trang báo lỗi HTTP 403, 404, 500
├── tests/                           # Bộ 14 Unit Test tự động (test_auth, test_catalog, test_cart...)
├── scripts/                         # Kịch bản kiểm thử lập trình mạng và nạp dữ liệu
│   ├── seed_data.py                 # Khởi tạo CSDL và nạp dữ liệu mẫu thực tế
│   ├── test_api_client.py           # Kịch bản gọi REST API JSON (Minh chứng CLO3)
│   └── test_mail_service.py         # Kịch bản kiểm tra định dạng và gửi email tự động (CLO2)
├── .env.example                     # Mẫu cấu hình biến môi trường an toàn
├── config.py                        # Cấu hình Development, Testing, Production
├── db.sqlite3                       # CSDL SQLite đã nạp sẵn dữ liệu hoa tươi và đơn hàng
├── requirements.txt                 # Danh mục thư viện Python cần cài đặt
├── run.py                           # Điểm khởi chạy máy chủ Flask Development
└── run_tests.py                     # Trình chạy toàn bộ 14 bài kiểm thử tự động
```

---

## 🚀 4. Hướng Dẫn Cài Đặt & Chạy Ứng Dụng (Windows PowerShell)

### Bước 1: Khởi tạo và kích hoạt môi trường ảo
```powershell
cd d:\shophoa-python

# Tạo môi trường ảo (nếu chưa có)
python -m venv venv

# Kích hoạt môi trường ảo
.\venv\Scripts\Activate.ps1
```

### Bước 2: Cài đặt các thư viện phụ thuộc
```powershell
pip install -r requirements.txt
```

### Bước 3: Thiết lập cấu hình môi trường `.env`
Sao chép từ file mẫu:
```powershell
Copy-Item .env.example .env
```
*(File `.env` mặc định đã được cấu hình chạy sẵn SQLite với đầy đủ dữ liệu mẫu).*

### Bước 4: (Tùy chọn) Nạp lại dữ liệu mẫu
```powershell
python scripts/seed_data.py
```

### Bước 5: Khởi chạy website Flask
```powershell
python run.py
```
Mở trình duyệt web truy cập các cổng thông tin:
- **Cửa hàng hoa (Khách hàng):** [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
- **Cổng Quản Trị Nghiệp Vụ (Admin/Staff):** [http://127.0.0.1:5000/dashboard/](http://127.0.0.1:5000/dashboard/)
- **REST API JSON (CLO3):** [http://127.0.0.1:5000/api/v1/products](http://127.0.0.1:5000/api/v1/products)

---

## 👥 5. Danh Sách Tài Khoản Thử Nghiệm

| Vai Trò | Tên Đăng Nhập | Mật Khẩu | Quyền Hạn & Chức Năng Trải Nghiệm |
| :--- | :--- | :--- | :--- |
| **Quản trị viên (Admin)** | `admin` | `admin123456` | Toàn quyền Dashboard: CRUD hoa tươi, xem biểu đồ doanh thu, duyệt đối soát thanh toán VietQR, quản lý kho hoa, quản lý mã ưu đãi, xuất báo cáo CSV |
| **Khách hàng thân thiết** | `khachhang1` | `customer123` | Lịch sử đặt 11 đơn hàng, lưu sẵn sổ địa chỉ, viết đánh giá hoa sau mua |
| **Khách hàng 2, 3, 4** | `khachhang2`, `khachhang3` | `customer123` | Các tài khoản khách hàng thực tế có chi tiêu và đơn hàng trên hệ thống |
| **Khách hàng mới** | *(Tùy ý đăng ký)* | *(Tùy ý)* | Đăng ký tài khoản mới trực tiếp qua giao diện `/accounts/register` |

> ⚠️ **Bảo mật nghiệp vụ:** Tài khoản Admin/Staff được ngăn chặn truy cập luồng mua hàng của khách để bảo toàn tính độc lập dữ liệu. Tài khoản khách hàng thông thường không được phép truy cập vào khu vực `/dashboard/` (báo lỗi 403 Forbidden).

---

## 🧪 6. Kiểm Thử Tự Động & Minh Chứng CLO

### 6.1. Chạy toàn bộ 14 Unit & Integration Tests
```powershell
python run_tests.py
```
*Kết quả:* **14/14 tests PASSED** trong ~2.2 giây (kiểm tra đầy đủ Auth, Catalog CRUD, Soft Delete, Giỏ hàng, Đặt hàng, Trừ/Hoàn tồn kho, Gửi Email, REST API).

### 6.2. Kiểm thử Lập trình mạng & REST API JSON (CLO3)
```powershell
python scripts/test_api_client.py
```
*Kết quả:* Mô phỏng ứng dụng client gọi HTTP đọc dữ liệu JSON từ máy chủ Flask (lấy danh sách hoa, tìm kiếm từ khóa, xem chi tiết mẫu hoa và xử lý lỗi 404).

### 6.3. Kiểm thử dịch vụ Email Flask-Mail (CLO2)
```powershell
python scripts/test_mail_service.py
```
*Kết quả:* Xác minh cấu hình SMTP, kiểm tra 4 kịch bản email tự động (xác nhận đơn hàng khách, thông báo đơn mới cho chủ shop `phuongtruong121204@gmail.com`, kích hoạt tài khoản và đặt lại mật khẩu).

---

*© FLORA FLOWER - Đồ án Lập trình Python Nâng cao - Khoa CNTT Trường Đại học Văn Lang.*
