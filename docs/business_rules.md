# TÀI LIỆU QUY TẮC NGHIỆP VỤ & BẢO TOÀN DỮ LIỆU (BUSINESS RULES)

## 1. Vòng Đời Đơn Hàng Hoa Tươi (Order Lifecycle & State Transitions)

Khác với đơn hàng thông thường chỉ có "Đang giao" và "Đã giao", quy trình bán hoa tươi tại **FLORA FLOWER** được chia thành 7 trạng thái chuyên nghiệp tương ứng với tiến trình làm việc tại xưởng hoa:

```
  [1. PENDING] ──(Khách đặt thành công)
       │
       ├─► (Thanh toán COD hoặc Đã tải Bill VietQR hợp lệ)
       │
  [2. CONFIRMED] ──(Nhân viên duyệt đơn / xác nhận)
       │
       ├─► (Chuyển lệnh cắm cho Florist, in Florist Sheet)
       │
  [3. PREPARING] ──(Florist đang cắm và bó hoa)
       │
       ├─► (Hoa cắm xong, kiểm tra độ tươi, thắt ruy băng, đính thiệp)
       │
  [4. READY_FOR_DELIVERY] ──(Sẵn sàng tại quầy xuất hàng)
       │
       ├─► (Bàn giao cho Shipper)
       │
  [5. DELIVERING] ──(Shipper đang trên đường vận chuyển)
       │
       ├─► (Giao tận tay người nhận, ký nhận / xác nhận)
       │
  [6. COMPLETED] ──(Hoàn tất đơn hàng)
       │
       └─► (Mở quyền cho khách hàng viết Đánh giá Verified Purchase)
```

### Quy tắc chuyển trạng thái đặc biệt:
- **Hủy đơn hàng (`CANCELLED`):**
  - **Khách hàng tự hủy:** Chỉ được phép khi đơn hàng đang ở trạng thái `PENDING` hoặc `CONFIRMED`. Khi đơn đã chuyển sang `PREPARING` (thợ hoa đã cắt gốc và cắm hoa), khách hàng **không được tự hủy trên web** mà phải liên hệ hotline trực tiếp.
  - **Nhân viên hủy:** Có thể hủy tại bất kỳ giai đoạn nào nếu phát hiện gian lận, khách không thanh toán hoặc địa chỉ không thể liên lạc được (bắt buộc nhập lý do hủy).
  - **Kích hoạt tự động khi hủy đơn:** Hệ thống lập tức gọi dịch vụ `record_order_cancellation(order)` trong `app/services/inventory.py` để trả lại số lượng hoa về kho, ghi nhận vào sổ cái `StockTransaction` với cờ `CANCEL_RESTORE` và bảo đảm tính Idempotent (không hoàn kho lặp lại).

---

## 2. Quy Tắc Giao Hàng & Khung Giờ (Delivery Date & Time Slots)

Hoa tươi là món quà mang tính thời điểm cao. Hệ thống áp dụng 4 quy tắc kiểm tra nghiêm ngặt khi khách chọn lịch giao:

1. **Quy tắc ngày giao không trong quá khứ:**
   $$\text{delivery\_date} \ge \text{today}$$
   Nếu khách chọn ngày trước hôm nay, hệ thống chặn ngay tại form validation của Flask-WTF.

2. **Quy tắc đặt hàng cùng ngày (Same-day Delivery Cutoff):**
   - Giờ cắt nhận đơn cùng ngày mặc định là **19:00** (cấu hình động tại `ShopSetting.same_day_cutoff_hour`).
   - Nếu thời gian đặt đơn hiện tại $> 19:00$, khách hàng bắt buộc phải chọn ngày giao từ ngày hôm sau trở đi.

3. **Thời gian chuẩn bị tối thiểu (Minimum Preparation Lead Time):**
   - Để đảm bảo hoa cắm đúng kỹ thuật và độ tươi, thời gian tối thiểu chuẩn bị hoa là **2 giờ** (`ShopSetting.min_prep_hours`).
   - Nếu giao trong cùng ngày, hệ thống tự động vô hiệu hóa các khung giờ quá sớm (Ví dụ: khách đặt lúc 10:30 sáng thì không thể chọn khung giờ Sáng `08:00 - 11:30`).

4. **Bốn Khung Giờ Tiêu Chuẩn Trong Ngày:**
   - `SLOT_1_MORNING`: 08:00 – 11:30 (Thích hợp cho hoa chúc mừng sự kiện đầu ngày, khai trương).
   - `SLOT_2_NOON`: 11:30 – 14:00 (Thích hợp cho bữa tiệc trưa, sinh nhật đồng nghiệp văn phòng).
   - `SLOT_3_AFTERNOON`: 14:00 – 17:30 (Thích hợp chúc mừng giờ hành chính, hoa tốt nghiệp).
   - `SLOT_4_EVENING`: 17:30 – 21:00 (Thích hợp cho tiệc tối lãng mạn, kỷ niệm).

---

## 3. Tách Biệt Người Đặt (Sender) & Người Nhận (Recipient)

- **Người Đặt (Sender):** Nhận email xác nhận giao dịch qua Flask-Mail, xem chi tiết hóa đơn tài chính và tiến hành thanh toán COD/VietQR.
- **Người Nhận (Recipient):** Nhận hoa, được shipper liên lạc khi giao hàng tận nơi.
- **Tùy chọn ẩn danh (`is_anonymous = True`):**
  - Khi khách chọn tặng hoa ẩn danh, trên thiệp và nhãn dán quà tặng sẽ **hoàn toàn giấu tên người gửi**.
  - Phiếu thợ cắm hoa và phiếu giao hàng hiển thị nhãn `[ẨN DANH]`, bảo vệ tính bất ngờ và sự riêng tư cho khách hàng.

---

## 4. Quản Lý Kho Theo Sổ Cái Giao Dịch (Stock Ledger Pattern)

Thay vì chỉ lưu một trường `stock` đơn thuần, hệ thống duy trì bảng sổ cái `inventory_stocktransaction` với 4 loại giao dịch:
1. `SALE`: Trừ kho khi khách đặt hàng thành công.
2. `CANCEL_RESTORE`: Hoàn trả số lượng hoa về kho khi đơn bị hủy.
3. `IMPORT`: Nhập thêm số lượng hoa tươi mới từ nhà vườn Đà Lạt.
4. `ADJUST`: Điều chỉnh kiểm kê hao hụt thực tế (hoa héo, hoa dập).

Mỗi bản ghi ghi lại:
- `variant_id`: Biến thể hoa tương ứng (Size S/M/L).
- `quantity_change`: Số lượng biến động (+/-).
- `balance_after`: Số lượng tồn kho sau giao dịch.
- `reason`: Lý do phát sinh giao dịch.
- `performed_by`: Nhân viên thực hiện thao tác.
- `reference_order_id`: Mã đơn hàng đối chiếu (nếu có).

---

## 5. Quy Trình Duyệt Biên Lai Thanh Toán Chuyển Khoản VietQR

1. Khi khách chọn phương thức chuyển khoản ngân hàng:
   - Hệ thống sinh mã VietQR động chuẩn NAPAS chứa số tiền chính xác và cú pháp chuyển khoản mang mã đơn hàng (`FL-YYYYMMDD-XXXX`).
   - Đơn hàng được gắn trạng thái `WAITING_VERIFICATION` (Chờ đối soát).
2. Khách hàng chụp ảnh biên lai ủy nhiệm chi và tải lên hệ thống (`/payments/<id>/upload-proof/`).
3. Nhân viên tại Dashboard (`/dashboard/payments/`):
   - Mở xem ảnh biên lai chuyển khoản qua view bảo mật (chỉ nhân viên và chủ đơn mới xem được).
   - Đối chiếu số tiền thực tế vào tài khoản ngân hàng của shop.
   - Nếu khớp -> Bấm **"Duyệt chuyển khoản"**: Trạng thái thanh toán chuyển sang `PAID`, đơn hàng tự động chuyển sang `CONFIRMED`.
   - Nếu bill không hợp lệ -> Bấm **"Từ chối bill"** kèm lý do gửi cho khách.

---

## 6. Phân Quyền & Hàng Rào An Toàn Nghiệp Vụ (RBAC Guards)

| Nhóm Tài Khoản | Phạm Vi Được Phép | Hàng Rào Bị Chặn Tuyệt Đối |
| :--- | :--- | :--- |
| **Khách hàng (Customer)** | Đặt hàng, xem đơn cá nhân, lưu sổ địa chỉ, đánh giá hoa đã mua, hủy đơn của mình khi chưa chuẩn bị. | Tuyệt đối **không được truy cập bất kỳ URL nào thuộc `/dashboard/`** (chặn bởi decorator `@staff_required` trả về 403 Forbidden). |
| **Nhân viên / Admin** | Truy cập `/dashboard/`, duyệt đơn, quản lý kho, đổi trạng thái, xem báo cáo Chart.js. | Tuyệt đối **không được đặt hàng bằng tài khoản nhân viên** tại giao diện khách hàng (chặn tại route `/orders/checkout/` để phòng ngừa đơn ảo). |
| **Admin duy nhất** | Cấu hình cửa hàng, phân quyền nhân sự, tạo voucher, xem AuditLog. | **Không thể tự hạ quyền hoặc tự khóa chính mình** nếu chỉ còn 1 tài khoản Admin duy nhất trong hệ thống. |
| **Tài khoản bị khóa (`is_locked`)** | Không thể đăng nhập vào hệ thống; phiên làm việc bị ngắt ngay lập tức. | Mọi yêu cầu đăng nhập đều bị từ chối kèm thông báo liên hệ ban quản trị. |

---

## 7. Quy Tắc Xóa Sản Phẩm & Biến Thể An Toàn (Safe Product Deletion & Soft Delete)

Trong thương mại điện tử thực chiến, việc xóa dữ liệu sản phẩm bất cẩn có thể phá hủy tính toàn vẹn của lịch sử kế toán và vi phạm ràng buộc khóa ngoại cơ sở dữ liệu. Hệ thống áp dụng 5 tầng bảo vệ nghiệp vụ:

### 7.1. Phân biệt Xóa Mềm (Soft Delete) vs Xóa Cứng (Hard Delete)
- Hệ thống xây dựng phương thức nghiệp vụ `product.can_be_hard_deleted()`:
  ```python
  def can_be_hard_deleted(self):
      from app.models.order import OrderItem
      variant_ids = [v.id for v in self.variants]
      if not variant_ids:
          return True
      has_orders = OrderItem.query.filter(OrderItem.product_variant_id.in_(variant_ids)).first()
      return has_orders is None
  ```
- **Trường hợp 1 (Sản phẩm đã có đơn hàng):**
  - Hệ thống **tự động chuyển sang cơ chế Xóa Mềm (Soft Delete / Archive)**: gọi `product.soft_delete()`, gán `product.status = 'ARCHIVED'`.
  - Sản phẩm lập tức bị ẩn khỏi toàn bộ danh mục mua sắm công khai và REST API.
  - Thông báo hiển thị cho nhân viên: *"Mẫu hoa này đã có đơn hàng trong quá khứ nên hệ thống đã tự động chuyển sang trạng thái LƯU TRỮ (Archived) để bảo toàn lịch sử hóa đơn tài chính."*
- **Trường hợp 2 (Sản phẩm mới chưa từng phát sinh đơn hàng):**
  - Hệ thống thực hiện Hard Delete: xóa sạch biến thể, xóa các bản ghi liên quan và tự động dọn dẹp file ảnh trong thư mục `media/` để giải phóng dung lượng đĩa.

### 7.2. Bảo toàn dữ liệu lịch sử hóa đơn (Snapshot Pattern)
- Trong bảng `orders_orderitem`, toàn bộ thông tin sản phẩm tại thời điểm chốt đơn gồm `product_name`, `variant_name`, `sku`, `unit_price`, `quantity`, `subtotal` được lưu cứng thành các trường độc lập.
- Khóa ngoại `OrderItem.product_variant_id` được thiết lập `ondelete='SET NULL'`.
- Khi biến thể bị thay đổi hoặc sản phẩm bị lưu trữ, toàn bộ hóa đơn cũ, phiếu thợ cắm hoa và số liệu doanh thu lịch sử vẫn nguyên vẹn 100%.

### 7.3. Quy tắc biến thể tối thiểu (Minimum Variant Rule)
- Mỗi mẫu hoa muốn bán được bắt buộc phải có ít nhất 1 kích thước/biến thể (Size S, Size M hoặc Size L).
- Khi nhân viên bấm xóa biến thể tại trang chỉnh sửa mẫu hoa:
  $$\text{product.variants.count()} \le 1 \implies \text{Hệ thống chặn xóa biến thể cuối cùng}$$
  Nhân viên phải giữ lại ít nhất một kích cỡ để đảm bảo sản phẩm luôn có giá bán và số lượng tồn kho hợp lệ.

### 7.4. Ghi nhận Nhật ký kiểm toán bắt buộc (Audit Trail)
- Mọi hành vi xóa sản phẩm hoặc xóa biến thể đều tự động phát sinh bản ghi kiểm toán trong bảng `AuditLog`:
  - `action`: `DELETE` hoặc `SOFT_DELETE`
  - `model_name`: `Product` hoặc `ProductVariant`
  - `user`: Tài khoản nhân viên thực hiện thao tác
  - `details`: Ghi rõ mã SKU, tên mẫu hoa và lý do lưu trữ.
- Dữ liệu này giúp chủ cửa hàng luôn truy vết được người chịu trách nhiệm cho mọi thay đổi trong danh mục hàng hóa.
