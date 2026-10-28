from datetime import datetime
from app.extensions import db

class StockTransaction(db.Model):
    __tablename__ = 'inventory_stocktransaction'

    id = db.Column(db.Integer, primary_key=True)
    variant_id = db.Column(db.BigInteger, db.ForeignKey('catalog_productvariant.id', ondelete='CASCADE'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # IMPORT, SALE, CANCEL_RESTORE, ADJUSTMENT
    quantity_change = db.Column(db.Integer, nullable=False)
    balance_after = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(255), default='', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    performed_by_id = db.Column(db.Integer, db.ForeignKey('auth_user.id'), nullable=True)
    reference_order_id = db.Column(db.BigInteger, db.ForeignKey('orders_order.id'), nullable=True)

    variant = db.relationship('ProductVariant', backref='stock_transactions')
    performed_by = db.relationship('User', foreign_keys=[performed_by_id])
    reference_order = db.relationship('Order', foreign_keys=[reference_order_id])

    @property
    def get_transaction_type_display(self):
        type_map = {
            'IMPORT': 'Nhập kho',
            'SALE': 'Xuất bán',
            'CANCEL_RESTORE': 'Hoàn tồn hủy đơn',
            'ADJUSTMENT': 'Kiểm kê điều chỉnh',
            'ORDER_RESERVE': 'Giữ hàng cho đơn',
            'ORDER_RELEASE': 'Xuất giao hàng'
        }
        return type_map.get(self.transaction_type, self.transaction_type)

    def __repr__(self):
        return f"<StockTransaction {self.transaction_type}: {self.quantity_change} (New Balance: {self.balance_after})>"

