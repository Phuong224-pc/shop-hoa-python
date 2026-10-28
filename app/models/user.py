import hashlib
import base64
from datetime import datetime
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from app.extensions import db, login_manager
from app.models.fields import ImageColumn

class User(UserMixin, db.Model):
    __tablename__ = 'auth_user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False, index=True)
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    password = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(150), default='', nullable=False)
    last_name = db.Column(db.String(150), default='', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_staff = db.Column(db.Boolean, default=False, nullable=False)
    is_superuser = db.Column(db.Boolean, default=False, nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)

    # Relationships
    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    addresses = db.relationship('Address', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    wishlist_items = db.relationship('Wishlist', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='customer', lazy='dynamic', foreign_keys='Order.user_id')

    @property
    def full_name(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return name if name else self.username

    @property
    def role(self):
        if self.is_superuser:
            return 'ADMIN'
        if self.profile and self.profile.role:
            return self.profile.role
        if self.is_staff:
            return 'STAFF'
        return 'CUSTOMER'

    def is_admin(self):
        return self.role == 'ADMIN' or self.is_superuser

    def is_store_staff(self):
        return self.role in ['ADMIN', 'STAFF'] or self.is_staff or self.is_superuser

    @property
    def is_staff_or_admin(self):
        return self.is_store_staff()

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        if not self.password:
            return False
        # 1. Check if password is stored in Django pbkdf2_sha256 format
        if self.password.startswith('pbkdf2_sha256$'):
            try:
                parts = self.password.split('$', 3)
                if len(parts) == 4:
                    _, iterations_str, salt, stored_hash = parts
                    iterations = int(iterations_str)
                    computed = hashlib.pbkdf2_hmac(
                        'sha256',
                        raw_password.encode('utf-8'),
                        salt.encode('utf-8'),
                        iterations
                    )
                    computed_b64 = base64.b64encode(computed).decode('ascii')
                    if computed_b64 == stored_hash:
                        # Auto-upgrade password to modern Werkzeug hash
                        self.set_password(raw_password)
                        try:
                            db.session.commit()
                        except Exception:
                            db.session.rollback()
                        return True
            except Exception:
                pass
            return False

        # 2. Werkzeug hash verification
        return check_password_hash(self.password, raw_password)

    # Token helpers
    def get_token(self, salt='auth-token', expires_sec=3600):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}, salt=salt)

    @staticmethod
    def verify_token(token, salt='auth-token', expires_sec=3600):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, salt=salt, max_age=expires_sec)
        except (SignatureExpired, BadTimeSignature):
            return None
        return db.session.get(User, data.get('user_id'))

    @property
    def is_staff_or_admin(self):
        return self.role in ['ADMIN', 'STAFF']

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class UserProfile(db.Model):
    __tablename__ = 'accounts_userprofile'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('auth_user.id'), nullable=False, unique=True)
    phone = db.Column(db.String(20), default='', nullable=False)
    avatar = db.Column(ImageColumn(200), nullable=True)
    gender = db.Column(db.String(1), default='O', nullable=False)  # M, F, O
    date_of_birth = db.Column(db.Date, nullable=True)
    role = db.Column(db.String(20), default='CUSTOMER', nullable=False)  # ADMIN, STAFF, CUSTOMER
    is_locked = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @property
    def is_staff_or_admin(self):
        return self.role in ['ADMIN', 'STAFF']

    def __repr__(self):
        return f"<UserProfile user_id={self.user_id} role={self.role}>"


class Address(db.Model):
    __tablename__ = 'accounts_address'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('auth_user.id'), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    street_address = db.Column(db.String(255), nullable=False)
    ward = db.Column(db.String(100), default='', nullable=False)
    district = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), default='TP. Hồ Chí Minh', nullable=False)
    is_default = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @property
    def formatted(self):
        parts = [self.street_address, self.ward, self.district, self.city]
        return ", ".join([p for p in parts if p])

    def __repr__(self):
        return f"<Address {self.full_name} - {self.formatted}>"


class Wishlist(db.Model):
    __tablename__ = 'accounts_wishlist'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('auth_user.id'), nullable=False)
    product_id = db.Column(db.BigInteger, db.ForeignKey('catalog_product.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    product = db.relationship('Product', backref='wishlist_entries')

    def __repr__(self):
        return f"<Wishlist user={self.user_id} product={self.product_id}>"
