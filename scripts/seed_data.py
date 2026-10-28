"""
FLORA FLOWER BOUTIQUE - SEED DATA SCRIPT (FLASK)
Khởi tạo CSDL SQLite với đầy đủ dữ liệu mẫu cho website Flora Flower.
Chạy: python scripts/seed_data.py
"""
import sys
import os
from pathlib import Path
from datetime import datetime, date, timedelta
from decimal import Decimal

# Add root directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from app import create_app, db
from app.models.user import User, UserProfile, Address
from app.models.catalog import (
    Category, Occasion, FlowerType, Accessory,
    Product, ProductVariant, ProductImage
)
from app.models.content import Banner, ContactMessage, FAQ
from app.models.core import ShopSetting, AuditLog
from app.models.promotion import Coupon
from app.models.order import Order, OrderItem, OrderItemAccessory, OrderStatusHistory
from app.models.payment import PaymentTransaction
from app.models.inventory import StockTransaction

app = create_app('development')

def seed():
    with app.app_context():
        print("Đang khởi tạo cấu trúc bảng CSDL...")
        db.create_all()

        # 1. Shop Setting
        setting = ShopSetting.query.first()
        if not setting:
            setting = ShopSetting(
                shop_name="Flora Flower Boutique",
                brand_slogan="Trao gửi yêu thương - Tươi sắc bốn mùa",
                hotline="1900 6868",
                zalo_phone="0903123456",
                email="contact@floraflower.vn",
                address="123 Hai Bà Trưng, Phường Bến Nghé, Quận 1, TP. Hồ Chí Minh",
                bank_code="MBBANK",
                bank_name="Ngân hàng Quân Đội (MB Bank)",
                bank_account_no="0903123456888",
                bank_account_name="NGUYEN THI MY LINH",
                shipping_fee_inner_city=Decimal('30000.00'),
                shipping_fee_suburban=Decimal('50000.00'),
                same_day_cutoff_hour=18,
                notification_email="phuongtruong121204@gmail.com"
            )
            db.session.add(setting)
            print("  + Đã tạo cấu hình cửa hàng ShopSetting")

        # 2. Users (Admin + Customers)
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@floraflower.vn',
                first_name='Quản Trị',
                last_name='Viên',
                is_active=True,
                is_staff=True,
                is_superuser=True
            )
            admin.set_password('admin123456')
            db.session.add(admin)
            db.session.flush()
            prof_admin = UserProfile(user_id=admin.id, phone='19006868', role='ADMIN')
            db.session.add(prof_admin)
            print("  + Đã tạo tài khoản Admin: admin / admin123456")

        customers = [
            ('khachhang1', 'khachhang1@floraflower.vn', 'Nguyễn Văn', 'An', '0903123456', '123 Lê Lợi', 'Phường Bến Nghé', 'Quận 1'),
            ('khachhang2', 'mai.tran@gmail.com', 'Trần Thị', 'Mai', '0909123456', '45 Nguyễn Thị Minh Khai', 'Phường Bến Nghé', 'Quận 1'),
            ('khachhang3', 'nam.le@gmail.com', 'Lê Hoàng', 'Nam', '0918765432', '78 Pasteur', 'Phường 6', 'Quận 3'),
            ('khachhang4', 'ha.pham@gmail.com', 'Phạm Thu', 'Hà', '0982345678', '12 Điện Biên Phủ', 'Phường 15', 'Quận Bình Thạnh'),
        ]
        for uname, email, fname, lname, phone, street, ward, district in customers:
            u = User.query.filter_by(username=uname).first()
            if not u:
                u = User(
                    username=uname,
                    email=email,
                    first_name=fname,
                    last_name=lname,
                    is_active=True,
                    is_staff=False,
                    is_superuser=False
                )
                u.set_password('customer123')
                db.session.add(u)
                db.session.flush()
                prof = UserProfile(user_id=u.id, phone=phone, role='CUSTOMER')
                db.session.add(prof)
                addr = Address(
                    user_id=u.id,
                    full_name=f"{fname} {lname}",
                    phone=phone,
                    street_address=street,
                    ward=ward,
                    district=district,
                    city='TP. Hồ Chí Minh',
                    is_default=True
                )
                db.session.add(addr)
                print(f"  + Đã tạo khách hàng: {uname} / customer123")

        # 3. Coupons
        sample_coupons = [
            ('FLORA10', 'Ưu đãi chào bạn mới giảm 10%', 'PERCENTAGE', Decimal('10.00'), Decimal('50000.00'), Decimal('200000.00')),
            ('WELCOME50K', 'Giảm trực tiếp 50.000đ cho đơn đầu tiên', 'FIXED_AMOUNT', Decimal('50000.00'), None, Decimal('300000.00')),
            ('VIPFLOWER', 'Giảm 15% tối đa 100k cho khách VIP', 'PERCENTAGE', Decimal('15.00'), Decimal('100000.00'), Decimal('500000.00')),
            ('TET2026', 'Ưu đãi mừng năm mới 2026 giảm 12%', 'PERCENTAGE', Decimal('12.00'), Decimal('80000.00'), Decimal('400000.00')),
        ]
        now = datetime.now()
        for code, title, dtype, val, max_val, min_amt in sample_coupons:
            cp = Coupon.query.filter_by(code=code).first()
            if not cp:
                cp = Coupon(
                    code=code,
                    title=title,
                    discount_type=dtype,
                    discount_value=val,
                    max_discount_amount=max_val,
                    min_order_amount=min_amt,
                    valid_from=now - timedelta(days=10),
                    valid_to=now + timedelta(days=90),
                    usage_limit=100,
                    is_active=True
                )
                db.session.add(cp)
                print(f"  + Đã tạo mã giảm giá: {code}")

        # 4. Contact Messages
        if ContactMessage.query.count() == 0:
            m1 = ContactMessage(
                full_name='Đỗ Thanh Tâm',
                email='tam.do@gmail.com',
                phone='0938112233',
                subject='Tư vấn hoa cưới tone pastel sang trọng',
                message='Chào shop, mình chuẩn bị tổ chức lễ cưới vào tháng sau tại GEM Center, muốn đặt trọn gói hoa cầm tay cô dâu, hoa cài áo và hoa bàn tiệc tone pastel. Shop tư vấn giúp mình nhé!',
                status='NEW',
                created_at=now - timedelta(hours=3)
            )
            m2 = ContactMessage(
                full_name='Công ty TNHH VinaTech',
                email='admin@vinatech.vn',
                phone='02838999888',
                subject='Đặt lẵng hoa khai trương chi nhánh có xuất hóa đơn VAT',
                message='Công ty chúng tôi cần đặt 2 kệ hoa chúc mừng khai trương đối tác vào thứ Sáu tuần này, tổng ngân sách khoảng 3 - 4 triệu đồng. Shop có xuất hóa đơn điện tử VAT được không?',
                status='PROCESSING',
                internal_notes='Đã gọi tư vấn, gửi profile mẫu hoa qua Zalo công ty',
                assigned_to_id=admin.id if admin else None,
                created_at=now - timedelta(days=1)
            )
            m3 = ContactMessage(
                full_name='Hoàng Lan Anh',
                email='lananh.hoang@yahoo.com',
                phone='0977665544',
                subject='Hỏi về nguồn gốc hoa Lan Hồ Điệp',
                message='Cho mình hỏi mẫu bình hoa Lan Hồ Điệp Bạch Ngọc bên bạn là lan giống Đài Loan hay Đà Lạt vậy ạ? Có bảo đảm độ tươi từ 3-4 tuần không shop?',
                status='RESOLVED',
                internal_notes='Đã giải đáp chi tiết về tiêu chuẩn lan A+ Đà Lạt và cách chăm sóc',
                assigned_to_id=admin.id if admin else None,
                created_at=now - timedelta(days=3)
            )
            db.session.add_all([m1, m2, m3])
            print("  + Đã tạo 3 tin nhắn liên hệ tư vấn khách hàng")

        db.session.commit()
        print("\n=> Khởi tạo dữ liệu mẫu Flora Flower thành công!")

if __name__ == '__main__':
    seed()
