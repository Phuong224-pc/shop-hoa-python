# BÁO CÁO TỔNG QUAN HỆ THỐNG WEBSITE HOA TƯƠI FLORA FLOWER
**Học phần:** Lập trình Python Nâng Cao (Mã HP: 71ITSE31003)  
**Giảng viên hướng dẫn:** ThS. Nguyễn Thị Mỹ Linh — Trường Đại học Văn Lang  
**Nền tảng công nghệ:** Python 3.11+, Flask Web Framework, Jinja2, Flask-SQLAlchemy, Flask-WTF, Flask-Mail, Flask-Login, SQLite/PostgreSQL  

---

## 1. Bối Cảnh Và Tính Cấp Thiết Của Đề Tài
Thị trường hoa tươi và điện hoa tại Việt Nam đang phát triển mạnh mẽ với xu hướng số hóa ngày càng rõ rệt. Tuy nhiên, phần lớn các website thương mại điện tử hiện nay được xây dựng dựa trên mô hình bán lẻ hàng hóa thông thường (quần áo, đồ gia dụng, thiết bị công nghệ), không đáp ứng được những đặc thù chuyên biệt của ngành hoa nghệ thuật:
- **Thời gian bảo quản ngắn (Perishable goods):** Hoa tươi không thể lưu kho lâu dài như hàng công nghiệp; việc quản lý tồn kho đòi hỏi theo dõi sát sao từng đợt hoa và kiểm soát thời gian chuẩn bị.
- **Người mua không phải người nhận:** Khác với việc mua sắm tự tiêu dùng, phần lớn khách hàng đặt hoa là để gửi tặng người thân, bạn bè, đối tác nhân các dịp đặc biệt (sinh nhật, khai trương, tốt nghiệp, kỷ niệm, chia buồn).
- **Yêu cầu nghiêm ngặt về thời gian và thông điệp:** Hoa tặng mang tính thời điểm cao. Giao muộn một khung giờ trong lễ khai trương hoặc sinh nhật làm mất toàn bộ ý nghĩa của món quà. Đi kèm mỗi bó hoa luôn là lời nhắn gửi, thiệp chúc mừng hoặc băng rôn in trang trọng.

Dự án **FLORA FLOWER** được nghiên cứu và hiện thực hóa bằng **ngôn ngữ lập trình Python** và nền tảng **Flask Web Framework** (Large Application Architecture) nhằm mang lại một giải pháp toàn diện: vừa là cửa hàng trực tuyến cao cấp phong cách boutique châu Âu, vừa là hệ thống quản trị vận hành bán lẻ hoa chuẩn mực cho các florist shop hiện đại, đáp ứng đầy đủ các chuẩn đầu ra (CLO1 - CLO5) của học phần.

---

## 2. Mục Tiêu Của Hệ Thống

### 2.1. Đối với Khách hàng (End Users):
- **Trải nghiệm mua sắm tinh tế, trang nhã:** Dễ dàng lựa chọn mẫu hoa theo kiểu dáng (Bó hoa, Giỏ hoa, Hộp hoa, Bình hoa, Kệ hoa) hoặc theo dịp tặng (Sinh nhật, Khai trương, Tình yêu, Cưới, Chia buồn).
- **Minh bạch kích cỡ & tồn kho:** Xem chi tiết biến thể kích thước (Size S - tiêu chuẩn, Size M - thịnh hành, Size L - cao cấp sang trọng), giá cập nhật tức thời và số lượng tồn kho theo thời gian thực.
- **Cá nhân hóa quà tặng:** Tùy chọn mua kèm phụ kiện (băng rôn, thiệp, hộp quà cao cấp), nhập lời chúc thiệp tặng và hỗ trợ tùy chọn gửi ẩn danh người tặng.
- **Lịch giao hoa chính xác:** Chọn ngày giao và 4 khung giờ giao trong ngày (Sáng, Trưa, Chiều, Tối) với thuật toán kiểm tra thời gian chuẩn bị tối thiểu và giờ chốt đơn cùng ngày.
- **Thanh toán đa dạng & Tra cứu nhanh:** Hỗ trợ COD và VietQR động chuẩn NAPAS; tra cứu tiến độ đơn hàng nhanh không cần đăng nhập bằng mã đơn và số điện thoại.

### 2.2. Đối với Đội ngũ Vận hành & Florist (Staff & Management):
- **Bảng điều khiển phân tích số liệu thời gian thực (Dashboard):** Thống kê doanh thu thuần, tiền thực thu, giá trị đơn trung bình (AOV), biểu đồ xu hướng doanh thu theo ngày và tỷ trọng đóng góp theo danh mục qua Chart.js.
- **Lịch giao hoa trực quan (Delivery Calendar):** Điều phối đơn theo ngày và khung giờ, tương phản cao, giao diện tiếng Việt rõ ràng.
- **Phiếu cắm hoa chuyên dụng (Florist Sheet):** In phiếu thợ cắm hoa bảo mật tuyệt đối giá tiền, chỉ hiển thị thông tin mẫu hoa, size, phụ kiện, ghi chú và lời chúc thiệp.
- **Quy trình duyệt đối soát biên lai chuyển khoản:** Khách hàng upload ảnh chứng từ chuyển khoản, nhân viên kiểm tra và duyệt một chạm.
- **Sổ cái kho hoa (Inventory Ledger):** Ghi nhận mọi giao dịch xuất bán (`SALE`), nhập kho (`IMPORT`), điều chỉnh (`ADJUST`) và hoàn trả kho chống trùng lặp (`CANCEL_RESTORE`).
- **Gửi email tự động qua Flask-Mail:** Tự động gửi email xác nhận đặt hàng kèm chi tiết đơn cho khách hàng và gửi thông báo đơn mới đến email quản trị cửa hàng (`SHOP_NOTIFICATION_EMAIL=phuongtruong121204@gmail.com`).
- **Cổng REST API công khai (CLO3):** Cung cấp các endpoint chuẩn JSON cho phép hệ thống bên ngoài tra cứu sản phẩm, tìm kiếm và xem chi tiết theo SKU.

---

## 3. Các Tác Nhân & Phân Quyền Trong Hệ Thống (RBAC)

```
                         ┌─────────────────────────────────────────┐
                         │              NGƯỜI DÙNG                 │
                         └────────────────────┬────────────────────┘
                                              │
                    ┌─────────────────────────┴─────────────────────────┐
                    │                                                   │
         ┌──────────▼──────────┐                             ┌──────────▼──────────┐
         │ KHÁCH HÀNG (Client) │                             │ NHÂN VIÊN & QUẢN TRỊ│
         └──────────┬──────────┘                             └──────────┬──────────┘
                    │                                                   │
         ┌──────────┴──────────┐              ┌───────────────┬─────────┴─────────┬────────────────┐
         │                     │              │               │                   │                │
┌────────▼────────┐   ┌────────▼────────┐┌────▼─────┐  ┌──────▼───────┐    ┌──────▼───────┐  ┌─────▼─────┐
│ Khách vãng lai  │   │ Khách đăng nhập ││  ADMIN   │  │  Nhân viên   │    │  Nhân viên   │  │ Nhân viên │
│ (Guest Session) │   │ (Customer User) ││ (Chủ shop│  │   Đơn hàng   │    │   Kho hoa    │  │ Nội dung  │
└─────────────────┘   └─────────────────┘└──────────┘  └──────────────┘    └──────────────┘  └───────────┘
```

1. **Khách hàng vãng lai (Guest):**
   - Duyệt xem danh mục hoa, sử dụng bộ lọc tìm kiếm theo từ khóa, giá, kiểu dáng, dịp tặng.
   - Thêm vào giỏ hàng session (Session Cart), áp dụng mã giảm giá, tra cứu tiến độ đơn hàng nhanh bằng mã đơn + số điện thoại.
2. **Khách hàng đã đăng ký (Registered Customer):**
   - Toàn bộ quyền lợi của khách vãng lai.
   - Tự động gộp giỏ hàng session vào tài khoản khi đăng nhập (Merge Cart).
   - Quản lý sổ địa chỉ giao hàng thân quen (`accounts_address`).
   - Lưu trữ danh sách hoa yêu thích (`accounts_wishlist`).
   - Xem lịch sử đơn hàng chi tiết, tải hóa đơn, tải ảnh biên lai chuyển khoản.
   - Viết đánh giá kèm số sao cho những mẫu hoa đã nhận thành công (Verified Purchase).
   - Tự hủy đơn hàng khi đơn chưa chuyển sang giai đoạn chuẩn bị cắm hoa.
3. **Quản trị viên Hệ thống (Unified Store Admin):**
   - Tài khoản quản trị toàn năng (`admin` / `admin123456`), truy cập Cổng Quản Trị `/dashboard/`.
   - Quản lý toàn bộ danh mục hoa, dịp tặng, phụ kiện và sản phẩm hoa tươi.
   - Quản lý vòng đời sản phẩm: Thêm, Sửa, và Xóa an toàn (Soft Delete/Archive với sản phẩm đã có đơn hàng nhằm bảo toàn lịch sử hóa đơn).
   - Quản lý đơn hàng, điều phối lịch giao hoa theo 4 khung giờ, in Phiếu thợ hoa và Hóa đơn khách hàng.
   - Quản lý kho hoa, nhập kho, đối soát biên lai VietQR.
   - Quản lý tài khoản người dùng, phân quyền nhân viên, cấu hình thông số cửa hàng và xem Audit Log.

---

## 4. Kiến Trúc Ứng Dụng Flask Chuẩn (Large Application Structure)

Hệ thống được tổ chức theo cấu trúc ứng dụng lớn chuẩn mực của Flask, đóng gói trong package `app/`, khởi tạo qua Application Factory `create_app()` và phân tách thành 8 Blueprints chuyên biệt:

```
shophoa-python/
├── app/
│   ├── __init__.py          # Application Factory create_app(), filter Jinja2, error handlers
│   ├── extensions.py        # Khởi tạo db, migrate, login_manager, mail, csrf
│   ├── jinja_compat.py      # Bộ mở rộng tương thích cú pháp template và filters
│   ├── models/              # Định nghĩa SQLAlchemy Models chuẩn ORM
│   │   ├── core.py          # ShopSetting, AuditLog
│   │   ├── user.py          # User, UserProfile, Address, Wishlist
│   │   ├── catalog.py       # Category, Occasion, FlowerType, Product, ProductVariant, Accessory
│   │   ├── cart.py          # Cart, CartItem, CartItemAccessory
│   │   ├── order.py         # Order, OrderItem, OrderItemAccessory, OrderStatusHistory
│   │   ├── payment.py       # PaymentTransaction, RefundRecord
│   │   ├── inventory.py     # StockTransaction
│   │   ├── promotion.py     # Coupon, CouponUsage
│   │   ├── review.py        # ProductReview
│   │   └── content.py       # Banner, PageContent, ContactMessage, FAQ
│   ├── forms/               # Flask-WTF Forms với validation & CSRF token
│   │   ├── auth.py          # LoginForm, RegisterForm, ProfileForm
│   │   ├── catalog.py       # ProductForm, ProductVariantForm, CategoryForm
│   │   ├── order.py         # CheckoutForm, OrderStatusForm
│   │   └── review.py        # ReviewForm
│   ├── services/            # Tầng xử lý logic nghiệp vụ độc lập
│   │   ├── email.py         # Dịch vụ gửi email thông báo qua Flask-Mail
│   │   ├── cart.py          # Dịch vụ quản lý giỏ hàng & merge session cart
│   │   └── inventory.py     # Dịch vụ xuất kho, hoàn tồn & ghi sổ cái
│   └── blueprints/          # 8 Blueprints theo từng module nghiệp vụ
│       ├── main.py          # Trang chủ, trang tĩnh, liên hệ, chính sách
│       ├── auth.py          # Đăng ký, đăng nhập, hồ sơ, địa chỉ, wishlist
│       ├── catalog.py       # Danh sách sản phẩm, chi tiết mẫu hoa, lọc, tìm kiếm
│       ├── cart.py          # Xem giỏ, thêm/sửa/xóa món, áp dụng mã ưu đãi
│       ├── orders.py        # Checkout, hoàn tất đặt đơn, tra cứu, hủy đơn
│       ├── reviews.py       # Gửi đánh giá cho sản phẩm đã mua
│       ├── dashboard.py     # Báo cáo Chart.js, lịch giao hoa, CRUD sản phẩm, kho, đơn
│       └── api.py           # REST API chuẩn JSON (CLO3) cho sản phẩm & phân trang
├── config.py                # Cấu hình môi trường Development, Testing, Production
├── run.py                   # Điểm khởi chạy ứng dụng Flask chính thức
├── scripts/
│   └── test_api_client.py   # Script kiểm thử kết nối REST API (requests / urllib)
├── tests/                   # Bộ kiểm thử tự động 14 test cases (unittest)
├── templates/               # Giao diện Jinja2 kế thừa base.html
├── static/                  # CSS Bootstrap 5.3, JavaScript, Webfonts, Icons
├── media/                   # Thư mục lưu trữ hình ảnh hoa và chứng từ thanh toán
├── docs/                    # Toàn bộ tài liệu báo cáo & thuyết trình đề tài
├── requirements.txt         # Danh mục thư viện phụ thuộc Python
└── .env.example             # Mẫu biến môi trường bảo mật
```

---

## 5. Giá Trị Thực Tiễn & Điểm Sáng Kỹ Thuật

1. **Tuân thủ 100% chuẩn Flask & Khung đánh giá đồ án:**
   - Ứng dụng phát triển hoàn toàn trên nền tảng **Flask**, sử dụng **Jinja2**, **Flask-SQLAlchemy**, **Flask-WTF** (bảo vệ CSRF cho mọi form), **Flask-Login** và **Flask-Mail**.
   - Phân tách rõ ràng giữa cấu hình, models, forms, services, blueprints và templates.
2. **Bảo toàn dữ liệu & Tương thích mật khẩu thông minh:**
   - Bảo toàn 100% cơ sở dữ liệu mẫu gồm hàng chục mẫu hoa thật, danh mục, dịp tặng, banner và đơn hàng lịch sử.
   - Cơ chế xác thực mật khẩu thông minh: hỗ trợ kiểm tra mật khẩu đã mã hóa theo chuẩn HMAC-PBKDF2 SHA-256 từ trước, sau đó tự động nâng cấp mượt mà lên mã băm chuẩn Werkzeug mà không làm gián đoạn tài khoản của người dùng.
3. **Cơ chế Xóa An Toàn (Soft Delete / Archive):**
   - Nghiệp vụ thực tế: Sản phẩm đã phát sinh đơn hàng trong quá khứ không được xóa cứng (hard delete) nhằm bảo vệ tính toàn vẹn của lịch sử mua bán và doanh thu.
   - Khi xóa sản phẩm đã có đơn hàng, hệ thống tự động chuyển trạng thái sang `ARCHIVED`, ẩn khỏi cửa hàng công khai nhưng vẫn hiển thị rõ ràng trên hóa đơn cũ và trong báo cáo quản trị.
4. **Lập trình mạng & REST API chuẩn mực (CLO3):**
   - Xây dựng REST API độc lập với các endpoint `GET /api/v1/products` (hỗ trợ tìm kiếm, lọc danh mục, phân trang) và `GET /api/v1/products/<id>`.
   - Đi kèm kịch bản Python client `scripts/test_api_client.py` sử dụng thư viện `requests` (kèm fallback `urllib`), có cơ chế xử lý ngoại lệ mạng, timeout và định dạng JSON chuyên nghiệp.
5. **Gửi email thông báo chuẩn xác qua Flask-Mail:**
   - Email xác nhận đơn hàng chuyên nghiệp gửi trực tiếp tới hòm thư người mua.
   - Email thông báo đơn hàng mới được gửi tự động tới địa chỉ quản trị cửa hàng: `SHOP_NOTIFICATION_EMAIL=phuongtruong121204@gmail.com`.
6. **Kiểm thử tự động toàn diện:**
   - Bộ kiểm thử tự động gồm **14/14 test cases** (`tests/test_*.py`) bao phủ toàn bộ luồng nghiệp vụ: Đăng ký/đăng nhập, CRUD sản phẩm, thêm giỏ hàng, checkout, hoàn tồn kho, bảo vệ CSRF, phân quyền RBAC, gửi email và REST API. Kết quả kiểm thử đạt **100% Passed**.
