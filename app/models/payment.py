from datetime import datetime
from decimal import Decimal
from app.extensions import db
from app.models.fields import ImageColumn

class PaymentTransaction(db.Model):
    __tablename__ = 'payments_paymenttransaction'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.BigInteger, db.ForeignKey('orders_order.id', ondelete='CASCADE'), nullable=False)
    payment_method = db.Column(db.String(20), default='COD', nullable=False)  # COD, BANK_TRANSFER
    status = db.Column(db.String(25), default='PENDING', nullable=False)  # PENDING, WAITING_VERIFICATION, PAID, FAILED, REFUNDED
    amount = db.Column(db.Numeric(12, 2), default=Decimal('0.00'), nullable=False)
    transaction_code = db.Column(db.String(80), default='', nullable=False)
    proof_image = db.Column(ImageColumn(200), nullable=True)
    proof_uploaded_at = db.Column(db.DateTime, nullable=True)
    verified_at = db.Column(db.DateTime, nullable=True)
    verified_by_id = db.Column(db.Integer, db.ForeignKey('auth_user.id'), nullable=True)
    rejection_reason = db.Column(db.Text, default='', nullable=False)
    notes = db.Column(db.Text, default='', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    verified_by = db.relationship('User', foreign_keys=[verified_by_id])
    refunds = db.relationship('RefundRecord', backref='payment', lazy='dynamic')

    @property
    def get_payment_method_display(self):
        method_map = {
            'COD': 'Tiền mặt khi nhận hoa (COD)',
            'BANK_TRANSFER': 'Chuyển khoản ngân hàng (VietQR)',
        }
        return method_map.get(self.payment_method, self.payment_method)

    @property
    def get_status_display(self):
        status_map = {
            'PENDING': 'Chờ thanh toán',
            'WAITING_VERIFICATION': 'Chờ đối soát biên lai',
            'PAID': 'Đã thanh toán',
            'FAILED': 'Thanh toán thất bại',
            'REFUNDED': 'Đã hoàn tiền'
        }
        return status_map.get(self.status, self.status)

    @property
    def proof_image_url(self):
        if not self.proof_image:
            return None
        if self.proof_image.startswith('http') or self.proof_image.startswith('/'):
            return self.proof_image
        return f"/media/{self.proof_image}"

    def __repr__(self):
        return f"<PaymentTransaction #{self.id} for Order {self.order_id} ({self.status})>"


class RefundRecord(db.Model):
    __tablename__ = 'payments_refundrecord'

    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.BigInteger, db.ForeignKey('payments_paymenttransaction.id'), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    reason = db.Column(db.Text, default='', nullable=False)
    refund_transaction_code = db.Column(db.String(100), default='', nullable=False)
    processed_by_id = db.Column(db.Integer, db.ForeignKey('auth_user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    processed_by = db.relationship('User', foreign_keys=[processed_by_id])

    def __repr__(self):
        return f"<RefundRecord #{self.id} for Payment {self.payment_id}: {self.amount}>"

