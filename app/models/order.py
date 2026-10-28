from datetime import datetime
from decimal import Decimal
from app.extensions import db

class Order(db.Model):
    __tablename__ = 'orders_order'

    TIME_SLOT_CHOICES = [
        ('08:00 - 10:00', '08:00 - 10:00 (Buổi sáng sớm)'),
        ('10:00 - 12:00', '10:00 - 12:00 (Buổi trưa)'),
        ('13:00 - 15:00', '13:00 - 15:00 (Đầu giờ chiều)'),
        ('15:00 - 17:00', '15:00 - 17:00 (Cuối giờ chiều)'),
        ('17:00 - 19:00', '17:00 - 19:00 (Đầu giờ tối)'),
        ('19:00 - 21:00', '19:00 - 21:00 (Buổi tối)'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Chờ xác nhận'),
        ('CONFIRMED', 'Đã xác nhận'),
        ('PREPARING', 'Đang cắm hoa / Chuẩn bị'),
        ('READY', 'Sẵn sàng giao'),
        ('DELIVERING', 'Đang giao hoa'),
        ('COMPLETED', 'Hoàn tất đơn hàng'),
        ('CANCELLED', 'Hủy đơn hàng'),
    ]

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    status = db.Column(db.String(20), default='PENDING', nullable=False, index=True)
    # PENDING, CONFIRMED, PREPARING, READY, DELIVERING, COMPLETED, CANCELLED
    delivery_method = db.Column(db.String(15), default='DELIVERY', nullable=False)
    sender_name = db.Column(db.String(120), nullable=False)
    sender_phone = db.Column(db.String(20), nullable=False)
    sender_email = db.Column(db.String(254), nullable=False)
    recipient_name = db.Column(db.String(120), nullable=False)
    recipient_phone = db.Column(db.String(20), nullable=False)
    delivery_address = db.Column(db.String(255), nullable=False)
    delivery_ward = db.Column(db.String(100), default='', nullable=False)
    delivery_district = db.Column(db.String(100), nullable=False)
    delivery_city = db.Column(db.String(100), default='TP. Hồ Chí Minh', nullable=False)
    delivery_date = db.Column(db.Date, nullable=False)
    delivery_time_slot = db.Column(db.String(30), nullable=False)
    card_message = db.Column(db.Text, default='', nullable=False)
    card_sender_name = db.Column(db.String(120), default='', nullable=False)
    is_anonymous = db.Column(db.Boolean, default=False, nullable=False)
    customer_notes = db.Column(db.Text, default='', nullable=False)
    internal_notes = db.Column(db.Text, default='', nullable=False)
    flowers_subtotal = db.Column(db.Numeric(12, 2), default=Decimal('0.00'), nullable=False)
    accessories_subtotal = db.Column(db.Numeric(12, 2), default=Decimal('0.00'), nullable=False)
    shipping_fee = db.Column(db.Numeric(12, 2), default=Decimal('0.00'), nullable=False)
    discount_amount = db.Column(db.Numeric(12, 2), default=Decimal('0.00'), nullable=False)
    total_amount = db.Column(db.Numeric(12, 2), default=Decimal('0.00'), nullable=False)
    coupon_code_snapshot = db.Column(db.String(50), default='', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    cancellation_reason = db.Column(db.Text, default='', nullable=False)
    cancelled_by_id = db.Column(db.Integer, db.ForeignKey('auth_user.id'), nullable=True)
    coupon_id = db.Column(db.BigInteger, db.ForeignKey('promotions_coupon.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('auth_user.id'), nullable=False)

    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    history = db.relationship('OrderStatusHistory', backref='order', lazy='dynamic', cascade='all, delete-orphan', order_by='OrderStatusHistory.created_at.desc()')
    transactions = db.relationship('PaymentTransaction', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    cancelled_by = db.relationship('User', foreign_keys=[cancelled_by_id])

    @property
    def payment(self):
        return self.transactions.order_by(db.desc('id')).first()

    @property
    def payment_status(self):
        latest = self.payment
        if not latest:
            return 'UNPAID'
        return latest.status

    @property
    def payment_method(self):
        latest = self.payment
        if not latest:
            return 'COD'
        return latest.payment_method

    @property
    def get_delivery_method_display(self):
        method_map = {
            'DELIVERY': 'Giao hoa tận nơi',
            'PICKUP': 'Nhận hoa tại cửa hàng'
        }
        return method_map.get(self.delivery_method, self.delivery_method)

    @property
    def get_status_display(self):
        status_map = {
            'PENDING': 'Chờ xác nhận',
            'CONFIRMED': 'Đã xác nhận',
            'PREPARING': 'Đang chuẩn bị hoa',
            'READY': 'Sẵn sàng giao',
            'DELIVERING': 'Đang giao hoa',
            'COMPLETED': 'Hoàn tất',
            'CANCELLED': 'Đã hủy'
        }
        return status_map.get(self.status, self.status)

    @property
    def is_cancellable_by_customer(self):
        return self.status in ['PENDING', 'CONFIRMED']

    @property
    def can_cancel_by_customer(self):
        return self.is_cancellable_by_customer

    @property
    def full_delivery_address(self):
        if self.delivery_method == 'PICKUP':
            return 'Nhận trực tiếp tại Cửa hàng Flora Flower'
        parts = [self.delivery_address, self.delivery_ward, self.delivery_district, self.delivery_city]
        return ", ".join([p for p in parts if p])

    def __repr__(self):
        return f"<Order #{self.order_number} ({self.status}) - {self.total_amount}>"


class OrderItem(db.Model):
    __tablename__ = 'orders_orderitem'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.BigInteger, db.ForeignKey('orders_order.id', ondelete='CASCADE'), nullable=False)
    product_variant_id = db.Column(db.BigInteger, db.ForeignKey('catalog_productvariant.id', ondelete='SET NULL'), nullable=True)
    product_name = db.Column(db.String(200), nullable=False)
    variant_name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(60), nullable=False)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)

    variant = db.relationship('ProductVariant', backref='order_items')
    accessories = db.relationship('OrderItemAccessory', backref='order_item', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def accessories_total(self):
        return sum(a.subtotal for a in self.accessories.all())

    @property
    def grand_item_total(self):
        return self.subtotal + self.accessories_total

    def __repr__(self):
        return f"<OrderItem #{self.id} for Order {self.order_id}: {self.product_name}>"


class OrderItemAccessory(db.Model):
    __tablename__ = 'orders_orderitemaccessory'

    id = db.Column(db.Integer, primary_key=True)
    order_item_id = db.Column(db.BigInteger, db.ForeignKey('orders_orderitem.id', ondelete='CASCADE'), nullable=False)
    accessory_id = db.Column(db.BigInteger, db.ForeignKey('catalog_accessory.id', ondelete='SET NULL'), nullable=True)
    accessory_name = db.Column(db.String(150), nullable=False)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)

    accessory = db.relationship('Accessory')

    def __repr__(self):
        return f"<OrderItemAccessory {self.accessory_name} x{self.quantity}>"


class OrderStatusHistory(db.Model):
    __tablename__ = 'orders_orderstatushistory'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.BigInteger, db.ForeignKey('orders_order.id', ondelete='CASCADE'), nullable=False)
    from_status = db.Column(db.String(20), nullable=False)
    to_status = db.Column(db.String(20), nullable=False)
    note = db.Column(db.String(255), default='', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    changed_by_id = db.Column(db.Integer, db.ForeignKey('auth_user.id'), nullable=True)

    changed_by = db.relationship('User')

    def __repr__(self):
        return f"<OrderStatusHistory #{self.order_id}: {self.from_status} -> {self.to_status}>"

