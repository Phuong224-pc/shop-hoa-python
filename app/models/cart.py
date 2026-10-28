from datetime import datetime
from decimal import Decimal
from app.extensions import db

class Cart(db.Model):
    __tablename__ = 'cart_cart'

    id = db.Column(db.Integer, primary_key=True)
    session_key = db.Column(db.String(100), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    coupon_id = db.Column(db.BigInteger, db.ForeignKey('promotions_coupon.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('auth_user.id'), nullable=True, index=True)

    items = db.relationship('CartItem', backref='cart', lazy='dynamic', cascade='all, delete-orphan')
    coupon = db.relationship('Coupon', backref='carts')

    @property
    def total_items_count(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def flowers_subtotal(self):
        total = Decimal('0.00')
        for item in self.items.all():
            if item.variant:
                total += Decimal(str(item.variant.effective_price)) * item.quantity
        return total

    @property
    def accessories_subtotal(self):
        total = Decimal('0.00')
        for item in self.items.all():
            total += item.accessories_total
        return total

    @property
    def subtotal_before_discount(self):
        return self.flowers_subtotal + self.accessories_subtotal

    @property
    def subtotal(self):
        return self.subtotal_before_discount

    @property
    def discount_amount(self):
        if not self.coupon or not self.coupon.is_valid():
            return Decimal('0.00')
        return self.coupon.calculate_discount(self.flowers_subtotal)

    @property
    def estimated_total(self):
        subtotal = self.flowers_subtotal + self.accessories_subtotal
        total = subtotal - self.discount_amount
        return max(Decimal('0.00'), total)

    def clear(self):
        for item in self.items.all():
            db.session.delete(item)
        self.coupon_id = None
        db.session.commit()

    def __repr__(self):
        return f"<Cart {self.id} (Items: {self.total_items_count})>"


class CartItem(db.Model):
    __tablename__ = 'cart_cartitem'

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.BigInteger, db.ForeignKey('cart_cart.id', ondelete='CASCADE'), nullable=False)
    variant_id = db.Column(db.BigInteger, db.ForeignKey('catalog_productvariant.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    card_message = db.Column(db.Text, default='', nullable=False)
    card_sender_name = db.Column(db.String(120), default='', nullable=False)
    is_anonymous = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    variant = db.relationship('ProductVariant', backref='cart_items')
    accessories = db.relationship('CartItemAccessory', backref='cart_item', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def accessories_total(self):
        total = Decimal('0.00')
        for acc in self.accessories.all():
            if acc.accessory:
                total += Decimal(str(acc.accessory.price)) * acc.quantity
        return total

    @property
    def line_total(self):
        flower_price = Decimal(str(self.variant.effective_price)) if self.variant else Decimal('0.00')
        return (flower_price * self.quantity) + self.accessories_total

    def __repr__(self):
        return f"<CartItem {self.id}: {self.variant_id} x{self.quantity}>"


class CartItemAccessory(db.Model):
    __tablename__ = 'cart_cartitemaccessory'

    id = db.Column(db.Integer, primary_key=True)
    cart_item_id = db.Column(db.BigInteger, db.ForeignKey('cart_cartitem.id', ondelete='CASCADE'), nullable=False)
    accessory_id = db.Column(db.BigInteger, db.ForeignKey('catalog_accessory.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)

    accessory = db.relationship('Accessory', backref='cart_usages')

    @property
    def total_price(self):
        if not self.accessory:
            return Decimal('0.00')
        return Decimal(str(self.accessory.price)) * self.quantity

    def __repr__(self):
        return f"<CartItemAccessory {self.accessory_id} x{self.quantity}>"

