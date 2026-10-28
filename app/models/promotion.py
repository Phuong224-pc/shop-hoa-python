from datetime import datetime
from decimal import Decimal
from app.extensions import db

class Coupon(db.Model):
    __tablename__ = 'promotions_coupon'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    discount_type = db.Column(db.String(10), default='PERCENTAGE', nullable=False)  # PERCENTAGE, FIXED_AMOUNT
    discount_value = db.Column(db.Numeric(12, 2), nullable=False)
    min_order_amount = db.Column(db.Numeric(12, 2), default=Decimal('0.00'), nullable=False)
    max_discount_amount = db.Column(db.Numeric(12, 2), nullable=True)
    valid_from = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    valid_to = db.Column(db.DateTime, nullable=False)
    usage_limit = db.Column(db.Integer, default=100, nullable=False)
    used_count = db.Column(db.Integer, default=0, nullable=False)
    per_user_limit = db.Column(db.Integer, default=1, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    usages = db.relationship('CouponUsage', backref='coupon', lazy='dynamic')

    def is_valid(self):
        now = datetime.utcnow()
        if not self.is_active:
            return False
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_to and now > self.valid_to:
            return False
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False
        return True

    def calculate_discount(self, order_amount):
        if not self.is_valid():
            return Decimal('0.00')
        if order_amount < self.min_order_amount:
            return Decimal('0.00')

        if self.discount_type == 'PERCENTAGE':
            discount = order_amount * (Decimal(str(self.discount_value)) / Decimal('100.00'))
            if self.max_discount_amount and discount > self.max_discount_amount:
                discount = self.max_discount_amount
        else:
            discount = min(order_amount, Decimal(str(self.discount_value)))

        return discount.quantize(Decimal('1.00'))

    def __repr__(self):
        return f"<Coupon {self.code} ({self.discount_value})>"


class CouponUsage(db.Model):
    __tablename__ = 'promotions_couponusage'

    id = db.Column(db.Integer, primary_key=True)
    coupon_id = db.Column(db.BigInteger, db.ForeignKey('promotions_coupon.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('auth_user.id'), nullable=False)
    order_id = db.Column(db.BigInteger, db.ForeignKey('orders_order.id'), nullable=True)
    discount_amount = db.Column(db.Numeric(12, 2), nullable=False)
    used_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref='coupon_usages')
    order = db.relationship('Order', backref='coupon_usages')

    def __repr__(self):
        return f"<CouponUsage {self.coupon_id} by user {self.user_id}>"

