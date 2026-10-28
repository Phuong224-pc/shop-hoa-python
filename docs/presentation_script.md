# KỊCH BẢN BÁO CÁO & THUYẾT TRÌNH BẢO VỆ ĐỒ ÁN (PRESENTATION & DEFENSE SCRIPT)

> **Đề tài:** Xây dựng Hệ thống Thương mại Điện tử Hoa tươi Cao cấp & Quản trị Nghiệp vụ Bán hoa **FLORA FLOWER**  
> **Học phần:** Lập trình Python Nâng Cao (Mã HP: 71ITSE31003) — Trường Đại học Văn Lang  
> **Giảng viên hướng dẫn:** ThS. Nguyễn Thị Mỹ Linh  
> **Ngôn ngữ & Nền tảng:** Python 3.11+ / Flask Web Framework (Large Application Structure)  
> **Thời lượng đề xuất:** 15 phút thuyết trình + 10 phút hỏi đáp (Q&A)

---

## 1. Dàn Ý Slide Báo Cáo (Slide Outline)

- **Slide 1: Trang tiêu đề:** Tên đề tài, sinh viên thực hiện, giảng viên hướng dẫn ThS. Nguyễn Thị Mỹ Linh, học phần Lập trình Python Nâng Cao.
- **Slide 2: Đặt vấn đề & Tính đặc thù của ngành hoa tươi:**
  - Hoa tươi là mặt hàng có hạn sử dụng ngắn, dễ hỏng, mang giá trị tinh thần và cảm xúc cao.
  - Người mua thường khác người nhận (tặng quà sinh nhật, khai trương, tốt nghiệp, tỏ tình, chia buồn).
  - Yêu cầu khắt khe về thời gian: chọn ngày giao, 4 khung giờ giao trong ngày, thông điệp trên thiệp chúc mừng, tùy chọn gửi ẩn danh.
- **Slide 3: Mục tiêu & Yêu cầu nghiệp vụ hệ thống:**
  - **Khách hàng:** Trải nghiệm mua hoa tinh tế, rõ ràng kích thước Size S/M/L, chọn phụ kiện đi kèm, giỏ hàng linh hoạt, thanh toán VietQR động chuẩn NAPAS hoặc COD.
  - **Cửa hàng:** Cổng quản trị Dashboard phân tích biểu đồ Chart.js, lịch giao hoa trực quan, in phiếu thợ cắm hoa bảo mật giá tiền, duyệt biên lai chuyển khoản VietQR, sổ cái kho hoa chống trùng lặp.
- **Slide 4: Kiến trúc công nghệ & Tổ chức mã nguồn (CLO1 & CLO2):**
  - Ngôn ngữ Python kết hợp kiến trúc ứng dụng lớn **Flask Large Application Structure**: Application Factory `create_app()`, 8 Blueprints độc lập (`main`, `auth`, `catalog`, `cart`, `orders`, `reviews`, `dashboard`, `api`).
  - ORM mạnh mẽ với **Flask-SQLAlchemy**, bảo vệ dữ liệu với transaction và rollback khi gặp sự cố.
  - Giao diện kế thừa **Jinja2** kết hợp Bootstrap 5.3 chuẩn responsive.
  - Biểu mẫu an toàn với **Flask-WTF** và mã thông báo bảo vệ CSRF trên mọi thao tác gửi dữ liệu.
- **Slide 5: Lập trình mạng & REST API (CLO3):**
  - Xây dựng hệ thống REST API trả về dữ liệu chuẩn JSON: `GET /api/v1/products` (hỗ trợ tìm kiếm, lọc danh mục, phân trang) và `GET /api/v1/products/<id>`.
  - Kịch bản kiểm thử độc lập `scripts/test_api_client.py` sử dụng thư viện `requests` (hỗ trợ fallback `urllib.request`), có timeout, kiểm tra mã HTTP status và bóc tách dữ liệu JSON.
- **Slide 6: Dịch vụ gửi Email tự động qua Flask-Mail (CLO4):**
  - Tích hợp **Flask-Mail** gửi email giao dịch HTML & văn bản thuần UTF-8.
  - Tự động gửi email xác nhận đặt hoa thành công tới hòm thư của khách hàng.
  - Tự động gửi email thông báo có đơn hàng mới tới địa chỉ quản trị cửa hàng: `SHOP_NOTIFICATION_EMAIL=phuongtruong121204@gmail.com`.
- **Slide 7: Những giải pháp kỹ thuật nổi bật:**
  - **Cơ chế Xóa An Toàn (Soft Delete / Archive):** Mẫu hoa đã có đơn hàng trong quá khứ được chuyển trạng thái `ARCHIVED` để bảo toàn lịch sử hóa đơn và số liệu tài chính; mẫu hoa chưa có đơn được xóa sạch (hard delete) kèm file ảnh liên quan.
  - **Idempotent Inventory Release:** Sổ cái kho hoa `StockTransaction` chống hoàn kho trùng lặp khi hủy đơn.
  - **Cart Merge thông minh:** Tự động gộp giỏ hàng vãng lai (Guest Session) vào tài khoản ngay khi đăng nhập.
  - **Phân quyền người dùng chặt chẽ (RBAC):** Khách hàng không thể vào Dashboard; nhân viên không được tự đặt hàng trên giao diện khách.
  - **Tương thích mật khẩu ngược:** Hỗ trợ xác thực mật khẩu cũ băm HMAC-PBKDF2 SHA-256 và tự động nâng cấp sang mã băm chuẩn Werkzeug.
- **Slide 8: DEMO TRỰC TIẾP HỆ THỐNG (Live Demo Flow).**
- **Slide 9: Kết quả kiểm thử tự động (Unit Test Suite):** 14/14 test cases passed 100% (Auth, Catalog CRUD, Giỏ hàng & Đơn hàng, Flask-Mail, REST API).
- **Slide 10: Lời cảm ơn & Sẵn sàng giải đáp câu hỏi của Hội đồng.**

---

## 2. Kịch Bản Thao Tác Demo Trực Tiếp (Live Demo Flow - 7 Phút)

### Phút 1 - 2: Khám Phá Cửa Hàng & Trải Nghiệm Khách Hàng (Storefront)
1. **Mở trình duyệt truy cập:** [http://127.0.0.1:5000/](http://127.0.0.1:5000/):
   - *"Kính thưa Hội đồng, đây là website bán hoa tươi FLORA FLOWER được nhóm phát triển hoàn toàn bằng ngôn ngữ Python và nền tảng Flask Web Framework theo kiến trúc Large Application Structure."*
   - Giới thiệu Banner slider hoa tươi sắc nét, thanh tìm kiếm mẫu hoa nhỏ gọn được tích hợp tinh tế trên thanh điều hướng chính (header).
   - Thử gõ tìm kiếm từ khóa *"Hồng"* hoặc duyệt theo Danh mục (Bó hoa, Giỏ hoa, Kệ hoa) và Dịp tặng (Sinh nhật, Khai trương, Tình yêu, Cưới, Chia buồn).
2. **Xem chi tiết mẫu hoa:**
   - Chọn mẫu hoa *"Bó Hoa Nắng Sớm Hồng Juliet"* hoặc *"Kệ Hoa Khai Trương"*.
   - Nhấp chọn lần lượt giữa các kích cỡ: **Size S (Tiêu chuẩn)**, **Size M (Vừa vặn)**, **Size L (Đặc biệt)**. Chỉ ra cho Hội đồng thấy giá bán, mã SKU và tồn kho tự động cập nhật ngay trên giao diện.
   - Tích chọn thêm phụ kiện bán kèm: *"Thiệp viết tay cao cấp"* và *"Băng rôn in chữ chúc mừng"*.
   - Bấm **"Thêm Vào Giỏ Hàng"**.

### Phút 3 - 4: Giỏ Hàng, Đặt Hàng & Thanh Toán VietQR Tự Động
1. **Tại trang Giỏ hàng (`/cart/`):**
   - Áp dụng mã ưu đãi: nhập mã voucher `FLORA10`, giỏ hàng lập tức chiết khấu giảm 10% và cập nhật thanh tiến trình miễn phí vận chuyển.
   - Trình bày tính năng gộp giỏ hàng (Cart Merge): Nếu khách thêm hoa khi chưa đăng nhập, sau khi đăng nhập tài khoản khách hàng, toàn bộ món hoa được tự động giữ nguyên và gộp vào tài khoản.
2. **Tiến hành đặt hoa (`/orders/checkout/`):**
   - Đăng nhập tài khoản khách hàng `khachhang1` (mật khẩu `customer123`).
   - Nhập thông tin Người Đặt: `Nguyễn Văn A` (0901234567).
   - Tích chọn: **"Người nhận là người khác"**.
   - Nhập thông tin Người Nhận: `Trần Thị B` (0987654321), Địa chỉ: `123 Lê Lợi, Phường Bến Nghé, Quận 1, TP. Hồ Chí Minh`.
   - Chọn ngày giao: Ngày mai. Chọn khung giờ giao: `14:00 - 17:30 (Chiều)`.
   - Nhập nội dung thiệp: *"Chúc mừng sinh nhật em gái yêu quý!"*.
   - Tích chọn: *"Gửi hoa ẩn danh (Không in tên người gửi lên thiệp)"*.
   - Chọn phương thức: **"Chuyển khoản ngân hàng qua VietQR"**.
   - Bấm **"Xác Nhận Đặt Đơn"**.
3. **Màn hình Đặt hàng thành công (`/orders/success/<order_number>`):**
   - Hiển thị mã đơn hàng (Ví dụ: `FL-20261028-XXXX`).
   - Mã VietQR được sinh ra tự động chuẩn NAPAS với số tiền chính xác và cú pháp chuyển khoản chứa mã đơn.
   - Hệ thống tự động kích hoạt **Flask-Mail**:
     + Gửi email xác nhận chi tiết đơn hàng đến hòm thư người mua.
     + Gửi email thông báo đơn mới đến email quản trị: `phuongtruong121204@gmail.com`.

### Phút 5 - 6: Cổng Quản Trị Nghiệp Vụ Vận Hành (Dashboard)
1. **Đăng nhập tài khoản Quản trị viên hợp nhất (`admin` / `admin123456`):**
   - Truy cập [http://127.0.0.1:5000/dashboard/](http://127.0.0.1:5000/dashboard/).
   - *"Thưa thầy cô, đây là Cổng quản trị Dashboard vận hành chuyên nghiệp được xây dựng trên Blueprint dashboard của Flask."*
   - Giới thiệu 4 thẻ chỉ số: Doanh thu thuần, Tiền thực thu, Tổng đơn hàng, Giá trị đơn trung bình (AOV).
   - Giới thiệu 3 biểu đồ trực quan hóa bằng Chart.js: Xu hướng doanh thu theo ngày, Trạng thái đơn hàng, và Doanh thu theo danh mục chính.
2. **Lịch giao hoa (`/dashboard/delivery-calendar/`):**
   - Cho Hội đồng xem thanh 7 ngày thông minh với định dạng thứ tiếng Việt ("Hôm nay", "Thứ 4", "Thứ 5"...), độ tương phản cao, màu sắc rõ ràng không bị đè chữ.
   - Đơn hàng vừa đặt xuất hiện chính xác vào cột khung giờ `14:00 - 17:30` của ngày mai.
3. **Mở chi tiết đơn hàng:**
   - Bấm **"In Phiếu Thợ Cắm Hoa (Florist Sheet)"**: Cho Hội đồng thấy tính năng đặc thù của shop hoa — phiếu thợ cắm hoa chỉ hiển thị mẫu hoa, kích thước, phụ kiện, ghi chú và lời chúc thiệp, **hoàn toàn ẩn giá tiền** để bảo mật và giữ sự tinh tế cho quà tặng.
   - Bấm **"In Hóa Đơn Khách Hàng (Customer Bill)"**: Hiển thị đầy đủ thông tin thanh toán và ẩn danh người gửi đúng theo yêu cầu.
4. **Quản lý Sản phẩm & Biến thể (`/dashboard/products/`):**
   - Trình diễn bộ công cụ CRUD: Thêm mới mẫu hoa, Sửa thông tin, và tính năng **Xóa an toàn**.
   - Trình bày cơ chế bảo vệ: Nếu sản phẩm đã phát sinh đơn hàng trong quá khứ, hệ thống tự động chuyển sang cơ chế **Xóa mềm (Soft Delete/Archive)** để bảo toàn lịch sử hóa đơn tài chính và tránh lỗi khóa ngoại database; nếu là sản phẩm mới chưa có đơn hàng, hệ thống thực hiện Hard Delete sạch sẽ.

### Phút 7: Trình Diễn Lập Trình Mạng & REST API (CLO3)
1. **Kiểm tra endpoint trên trình duyệt hoặc Postman:**
   - Mở [http://127.0.0.1:5000/api/v1/products](http://127.0.0.1:5000/api/v1/products) để xem danh sách sản phẩm trả về định dạng JSON chuẩn mực với đầy đủ thông tin phân trang `pagination` (trang hiện tại, tổng trang, tổng sản phẩm).
   - Mở [http://127.0.0.1:5000/api/v1/products/1](http://127.0.0.1:5000/api/v1/products/1) để xem chi tiết một mẫu hoa kèm toàn bộ biến thể kích cỡ và đánh giá.
2. **Chạy script kiểm thử mạng tự động:**
   - Mở terminal chạy lệnh: `python scripts/test_api_client.py`
   - *"Thưa thầy cô, đây là script Python độc lập sử dụng thư viện `requests` (kèm fallback `urllib`) để gọi HTTP đến API của Flask, đọc dữ liệu JSON, kiểm tra tìm kiếm từ khóa, kiểm tra mã phản hồi 200 OK và 404 Not Found, xử lý lỗi timeout và rớt mạng theo đúng chuẩn đầu ra CLO3."*
   - Kết quả hiển thị: **TẤT CẢ ENDPOINT ĐẠT CHUẨN 100%!**

---

## 3. Bộ Câu Hỏi Vấn Đáp Thường Gặp Của Hội Đồng (Q&A Defense)

### Câu 1: Tại sao nhóm lựa chọn kiến trúc Large Application Structure cho Flask mà không viết toàn bộ trong một file app.py duy nhất?
**Trả lời:**
*"Thưa thầy/cô, Flask là một micro-framework rất linh hoạt. Nếu chỉ viết trong một file `app.py`, mã nguồn sẽ nhanh chóng phình to, dễ bị phụ thuộc vòng (circular imports) và rất khó bảo trì khi dự án phát triển.
Nhóm đã áp dụng chuẩn kiến trúc Large Application Structure của Flask:
1. Sử dụng mô hình Application Factory `create_app()` trong `app/__init__.py`, cho phép khởi tạo ứng dụng độc lập với các môi trường cấu hình khác nhau (Development, Testing, Production).
2. Tách biệt hoàn toàn các mảng nghiệp vụ thành 8 Blueprints độc lập (`main`, `auth`, `catalog`, `cart`, `orders`, `reviews`, `dashboard`, `api`).
3. Khởi tạo các phần mở rộng (`db`, `migrate`, `login_manager`, `mail`, `csrf`) độc lập trong `app/extensions.py` và liên kết bằng phương thức `init_app(app)`.
Cấu trúc này giúp mã nguồn rõ ràng, dễ viết kiểm thử tự động và sẵn sàng mở rộng quy mô trong môi trường thực tế."*

### Câu 2: Hệ thống xử lý bảo mật biểu mẫu (Form Security) và tấn công CSRF như thế nào?
**Trả lời:**
*"Thưa thầy/cô, hệ thống sử dụng thư viện **Flask-WTF** kết hợp extension `CSRFProtect`:
1. Mọi biểu mẫu thay đổi trạng thái (POST) như đăng ký, đăng nhập, thêm/sửa sản phẩm, checkout đều được tạo từ các lớp form kế thừa `flask_wtf.FlaskForm`.
2. Trong template Jinja2, mỗi form đều được nhúng thẻ ẩn CSRF token qua `{{ form.hidden_tag() }}` hoặc `{% csrf_token %}`. Khi người dùng submit, Flask-WTF tự động đối soát token được ký mật mã với session để ngăn chặn triệt để tấn công giả mạo yêu cầu chéo trang (Cross-Site Request Forgery).
3. Đối với các endpoint REST API công khai phục vụ ứng dụng di động hoặc script khách hàng ngoài (`/api/v1/`), nhóm sử dụng decorator `@csrf.exempt` để các request HTTP tiêu chuẩn không bị chặn bởi token giao diện."*

### Câu 3: Làm thế nào để đảm bảo số lượng tồn kho hoa không bị lỗi khi khách hủy đơn hoặc nhiều người cùng mua?
**Trả lời:**
*"Thưa thầy/cô, hệ thống áp dụng 2 nguyên tắc kỹ thuật chuẩn:
1. **Giao dịch nguyên tử (ACID Transaction):** Trong SQLAlchemy, các thao tác tạo đơn hàng và trừ kho được bọc trong giao dịch cơ sở dữ liệu. Nếu phát sinh lỗi hoặc số lượng tồn không đủ (`stock < quantity`), hệ thống thực hiện `db.session.rollback()`, đảm bảo dữ liệu không bị ghi nhận dở dang và không xảy ra hiện tượng âm kho.
2. **Sổ cái kho hoa (Ledger Pattern) & Tính Idempotent:** Mỗi lần trừ kho hoặc hoàn kho đều phát sinh bản ghi lịch sử trong bảng `inventory_stocktransaction` với các loại giao dịch rõ ràng (`SALE`, `CANCEL_RESTORE`, `IMPORT`, `ADJUST`). Khi hủy đơn, hệ thống kiểm tra xem đơn hàng đã từng được hoàn kho hay chưa. Nếu đã hoàn kho rồi, hệ thống từ chối hoàn lặp lại, ngăn chặn lỗi cộng dồn tồn kho khi bấm hủy nhiều lần."*

### Câu 4: Khi xóa một mẫu hoa đã có khách mua trong quá khứ, làm sao hệ thống bảo toàn được dữ liệu lịch sử hóa đơn?
**Trả lời:**
*"Thưa thầy/cô, đây là bài toán nghiệp vụ kinh điển trong thương mại điện tử:
1. Nếu thực hiện Hard Delete (xóa hẳn khỏi database), cơ sở dữ liệu sẽ báo lỗi ràng buộc khóa ngoại (Foreign Key Constraint Violation) do bảng `orders_orderitem` đang tham chiếu đến sản phẩm đó, hoặc nếu dùng `CASCADE` thì toàn bộ lịch sử mua hàng và doanh thu quá khứ sẽ bị biến mất.
2. Nhóm đã hiện thực phương thức `product.can_be_hard_deleted()`:
   - Nếu sản phẩm chưa từng có đơn hàng nào, hệ thống cho phép Hard Delete và tự động xóa ảnh liên quan trong thư mục `media/`.
   - Nếu sản phẩm đã có đơn hàng, hệ thống tự động kích hoạt cơ chế **Xóa mềm (Soft Delete/Archive)**: chuyển trạng thái `status = 'ARCHIVED'`. Sản phẩm lập tức bị ẩn khỏi cửa hàng công khai, người dùng không thể tìm kiếm hay thêm vào giỏ, nhưng các đơn hàng cũ vẫn hiển thị đầy đủ tên hoa, giá tiền và hình ảnh, bảo đảm tính toàn vẹn 100% của báo cáo tài chính."*

### Câu 5: Yếu tố Lập trình mạng (CLO3) được nhóm thể hiện như thế nào trong đồ án?
**Trả lời:**
*"Thưa thầy/cô, nhóm đáp ứng chuẩn đầu ra CLO3 thông qua hai thành phần:
1. **Phía Server (REST API):** Xây dựng Blueprint `api` cung cấp các endpoint chuẩn RESTful trả về JSON:
   - `GET /api/v1/products`: Trả về danh sách hoa tươi, hỗ trợ tham số truy vấn tìm kiếm `?q=...`, lọc danh mục `?category_id=...` và phân trang `?page=...&per_page=...`.
   - `GET /api/v1/products/<id>`: Trả về chi tiết đầy đủ của một mẫu hoa, bao gồm toàn bộ biến thể kích thước và đánh giá khách hàng.
   - Các endpoint đều xử lý mã HTTP status chuẩn: `200 OK`, `404 Not Found` (trả về thông báo JSON có cấu trúc khi ID không tồn tại), `500 Internal Server Error`.
2. **Phía Client (Network Script):** Nhóm xây dựng kịch bản Python độc lập `scripts/test_api_client.py` sử dụng thư viện `requests` (kèm fallback `urllib.request` của thư viện chuẩn Python). Script thực hiện kết nối HTTP qua mạng tới server Flask, cấu hình timeout để tránh treo kết nối, xử lý ngoại lệ `ConnectionError` và bóc tách dữ liệu JSON để in báo cáo kiểm thử trực quan."*

### Câu 6: Dịch vụ gửi Email qua Flask-Mail được cấu hình và vận hành ra sao?
**Trả lời:**
*"Thưa thầy/cô, nhóm sử dụng thư viện **Flask-Mail**:
1. Cấu hình linh hoạt qua biến môi trường trong file `.env`: `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USE_TLS`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `SHOP_NOTIFICATION_EMAIL`.
2. Nhóm phân biệt rõ ràng hai luồng email:
   - **Email giao dịch khách hàng:** Gửi hóa đơn xác nhận đơn hàng tới địa chỉ email của người đặt hoa.
   - **Email quản trị cửa hàng:** Gửi thông báo đơn hàng mới tới email của chủ shop được chỉ định tại biến `SHOP_NOTIFICATION_EMAIL` (cụ thể là `phuongtruong121204@gmail.com`).
3. Nội dung email được thiết kế bằng template HTML tiếng Việt trang nhã kết hợp bản văn bản thuần (plain text) dự phòng, bảo đảm hiển thị đẹp mắt trên mọi ứng dụng đọc thư."*

### Câu 7: Nhóm đã thực hiện kiểm thử tự động (Automated Testing) cho hệ thống như thế nào?
**Trả lời:**
*"Thưa thầy/cô, nhóm đã xây dựng bộ kiểm thử tự động hoàn chỉnh sử dụng module `unittest` của Python trong thư mục `tests/`:
- `test_auth.py`: Kiểm thử luồng đăng ký, đăng nhập, bảo vệ mật khẩu và phân quyền RBAC.
- `test_catalog_crud.py`: Kiểm thử đầy đủ quy trình Thêm, Xem, Sửa, Xóa an toàn sản phẩm hoa và tìm kiếm.
- `test_cart_order.py`: Kiểm thử tính toán giỏ hàng, áp dụng voucher, checkout và hoàn kho khi hủy đơn.
- `test_mail.py`: Bắt và kiểm tra nội dung email gửi đi trong môi trường test mà không spam email thật.
- `test_api.py`: Kiểm thử toàn bộ các endpoint REST API (danh sách, tìm kiếm, chi tiết, mã lỗi 404).
Toàn bộ **14/14 test cases** đều vượt qua (100% Passed) trong thời gian dưới 5 giây."*
