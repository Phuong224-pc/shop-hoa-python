from datetime import datetime
from app.extensions import db

class ProductReview(db.Model):
    __tablename__ = 'reviews_productreview'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.BigInteger, db.ForeignKey('catalog_product.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('auth_user.id'), nullable=False)
    order_id = db.Column(db.BigInteger, db.ForeignKey('orders_order.id'), nullable=False)
    rating = db.Column(db.SmallInteger, default=5, nullable=False)
    comment = db.Column(db.Text, default='', nullable=False)
    status = db.Column(db.String(15), default='PENDING', nullable=False)  # PENDING, APPROVED, REJECTED
    admin_response = db.Column(db.Text, default='', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref='reviews')
    order = db.relationship('Order', backref='reviews')

    def __repr__(self):
        return f"<ProductReview #{self.id} for Product {self.product_id} (Rating: {self.rating})>"

