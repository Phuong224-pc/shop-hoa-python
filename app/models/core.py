from datetime import datetime
from decimal import Decimal
from app.extensions import db

class ShopSetting(db.Model):
    __tablename__ = 'core_shopsetting'

    id = db.Column(db.Integer, primary_key=True)
    shop_name = db.Column(db.String(150), default='Flora Flower Boutique', nullable=False)
    slogan = db.Column(db.String(255), default='Trao gửi yêu thương - Tinh tế trong từng cánh hoa', nullable=False)
    phone = db.Column(db.String(30), default='0901 234 567', nullable=False)
    hotline = db.Column(db.String(30), default='1900 6868', nullable=False)
    email = db.Column(db.String(254), default='contact@floraflower.vn', nullable=False)
    address = db.Column(db.String(255), default='123 Nguyễn Huệ, Phường Bến Nghé, Quận 1, TP. Hồ Chí Minh', nullable=False)
    opening_hours = db.Column(db.String(120), default='07:30 - 21:30 hàng ngày', nullable=False)
    facebook_url = db.Column(db.String(200), default='https://facebook.com/floraflower', nullable=False)
    instagram_url = db.Column(db.String(200), default='https://instagram.com/floraflower', nullable=False)
    zalo_phone = db.Column(db.String(30), default='0901234567', nullable=False)
    bank_code = db.Column(db.String(20), default='MB', nullable=False)
    bank_name = db.Column(db.String(100), default='Ngân hàng Quân Đội (MB Bank)', nullable=False)
    bank_account_no = db.Column(db.String(50), default='999988886666', nullable=False)
    bank_account_name = db.Column(db.String(100), default='CONG TY TNHH FLORA FLOWER', nullable=False)
    shipping_fee_default = db.Column(db.Numeric(12, 2), default=Decimal('30000.00'), nullable=False)
    free_shipping_threshold = db.Column(db.Numeric(12, 2), default=Decimal('500000.00'), nullable=False)
    min_prep_hours = db.Column(db.Integer, default=2, nullable=False)
    same_day_cutoff_hour = db.Column(db.Integer, default=18, nullable=False)
    max_orders_per_slot = db.Column(db.Integer, default=10, nullable=False)
    enable_store_pickup = db.Column(db.Boolean, default=True, nullable=False)
    enable_vietqr = db.Column(db.Boolean, default=True, nullable=False)
    enable_cod = db.Column(db.Boolean, default=True, nullable=False)
    seasonal_policy_text = db.Column(db.Text, default='', nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @staticmethod
    def get_settings():
        setting = ShopSetting.query.first()
        if not setting:
            setting = ShopSetting()
            db.session.add(setting)
            db.session.commit()
        return setting

    def __repr__(self):
        return f"<ShopSetting {self.shop_name}>"


class AuditLog(db.Model):
    __tablename__ = 'core_auditlog'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('auth_user.id'), nullable=True)
    action = db.Column(db.String(30), nullable=False)  # CREATE, UPDATE, DELETE, LOGIN, EXPORT
    model_name = db.Column(db.String(80), nullable=False)
    object_id = db.Column(db.String(80), default='', nullable=False)
    object_repr = db.Column(db.String(255), default='', nullable=False)
    details = db.Column(db.Text, default='', nullable=False)
    ip_address = db.Column(db.String(39), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', foreign_keys=[user_id])

    @staticmethod
    def log(user, action, model_name, object_id, object_repr='', details='', ip=None):
        entry = AuditLog(
            user_id=user.id if user and user.is_authenticated else None,
            action=action,
            model_name=model_name,
            object_id=str(object_id),
            object_repr=str(object_repr)[:255],
            details=details,
            ip_address=ip
        )
        db.session.add(entry)
        db.session.commit()

    def __repr__(self):
        return f"<AuditLog {self.action} on {self.model_name} #{self.object_id}>"

