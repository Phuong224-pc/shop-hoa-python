from datetime import datetime
from decimal import Decimal
from app.extensions import db
from app.models.fields import ImageColumn

# Association tables for Many-to-Many
product_occasions = db.Table(
    'catalog_product_occasions',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('product_id', db.BigInteger, db.ForeignKey('catalog_product.id', ondelete='CASCADE'), nullable=False),
    db.Column('occasion_id', db.BigInteger, db.ForeignKey('catalog_occasion.id', ondelete='CASCADE'), nullable=False)
)

product_flower_types = db.Table(
    'catalog_product_flower_types',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('product_id', db.BigInteger, db.ForeignKey('catalog_product.id', ondelete='CASCADE'), nullable=False),
    db.Column('flowertype_id', db.BigInteger, db.ForeignKey('catalog_flowertype.id', ondelete='CASCADE'), nullable=False)
)


class Category(db.Model):
    __tablename__ = 'catalog_category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, default='', nullable=False)
    image = db.Column(ImageColumn(200), nullable=True)
    icon = db.Column(db.String(50), default='bi-flower1', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    display_order = db.Column(db.Integer, default=0, nullable=False)

    products = db.relationship('Product', backref='primary_category', lazy='dynamic', foreign_keys='Product.primary_category_id')

    @property
    def active_products_count(self):
        return self.products.filter(Product.status == 'PUBLISHED').count()

    def __repr__(self):
        return f"<Category {self.name}>"


class Occasion(db.Model):
    __tablename__ = 'catalog_occasion'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, default='', nullable=False)
    image = db.Column(ImageColumn(200), nullable=True)
    icon = db.Column(db.String(50), default='bi-heart', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    display_order = db.Column(db.Integer, default=0, nullable=False)

    def __repr__(self):
        return f"<Occasion {self.name}>"


class FlowerType(db.Model):
    __tablename__ = 'catalog_flowertype'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, default='', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<FlowerType {self.name}>"


class Accessory(db.Model):
    __tablename__ = 'catalog_accessory'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Numeric(12, 2), default=Decimal('0.00'), nullable=False)
    image = db.Column(ImageColumn(200), nullable=True)
    description = db.Column(db.Text, default='', nullable=False)
    stock = db.Column(db.Integer, default=100, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    display_order = db.Column(db.Integer, default=0, nullable=False)

    def __repr__(self):
        return f"<Accessory {self.name} - {self.price}>"


class Product(db.Model):
    __tablename__ = 'catalog_product'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)
    main_image = db.Column(ImageColumn(200), default='', nullable=True)
    presentation_style = db.Column(db.String(20), default='BOUQUET', nullable=False)
    color_tone = db.Column(db.String(20), default='MIXED', nullable=False)
    short_description = db.Column(db.String(300), default='', nullable=False)
    description = db.Column(db.Text, default='', nullable=False)
    flower_composition = db.Column(db.String(350), default='', nullable=False)
    care_instructions = db.Column(db.Text, default='', nullable=False)
    seasonal_policy_notes = db.Column(db.Text, default='', nullable=False)
    status = db.Column(db.String(20), default='PUBLISHED', nullable=False)  # PUBLISHED, DRAFT, ARCHIVED
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    is_bestseller_manual = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    primary_category_id = db.Column(db.BigInteger, db.ForeignKey('catalog_category.id'), nullable=False)

    # Relationships
    variants = db.relationship('ProductVariant', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    gallery_images = db.relationship('ProductImage', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    occasions = db.relationship('Occasion', secondary=product_occasions, backref=db.backref('products', lazy='dynamic'))
    flower_types = db.relationship('FlowerType', secondary=product_flower_types, backref=db.backref('products', lazy='dynamic'))
    reviews = db.relationship('ProductReview', backref='product', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def is_active(self):
        return self.status == 'PUBLISHED'

    @property
    def is_archived(self):
        return self.status == 'ARCHIVED'

    @property
    def default_variant(self):
        v = self.variants.filter_by(is_default=True).first()
        if not v:
            v = self.variants.first()
        return v

    @property
    def min_price(self):
        prices = [v.effective_price for v in self.variants.all() if v.effective_price is not None]
        return min(prices) if prices else Decimal('0.00')

    @property
    def max_price(self):
        prices = [v.effective_price for v in self.variants.all() if v.effective_price is not None]
        return max(prices) if prices else Decimal('0.00')

    @property
    def total_stock(self):
        return sum([v.stock for v in self.variants.all()])

    @property
    def in_stock(self):
        return self.total_stock > 0

    @property
    def main_image_url(self):
        if not self.main_image:
            return '/static/images/placeholder-flower.jpg'
        if self.main_image.startswith('http') or self.main_image.startswith('/'):
            return self.main_image
        return f"/media/{self.main_image}"

    @property
    def average_rating(self):
        approved = self.reviews.filter_by(status='APPROVED').all()
        if not approved:
            return 5.0
        return round(sum(r.rating for r in approved) / len(approved), 1)

    @property
    def approved_reviews_count(self):
        return self.reviews.filter_by(status='APPROVED').count()

    @property
    def total_sold_count(self):
        from app.models.order import OrderItem, Order
        sold = db.session.query(db.func.sum(OrderItem.quantity))\
            .join(Order, Order.id == OrderItem.order_id)\
            .join(ProductVariant, ProductVariant.id == OrderItem.product_variant_id)\
            .filter(ProductVariant.product_id == self.id)\
            .filter(Order.status.in_(['COMPLETED', 'DELIVERING', 'READY', 'PREPARING', 'CONFIRMED']))\
            .scalar()
        return sold or 0

    def can_be_hard_deleted(self):
        """Check if any orders reference this product's variants."""
        from app.models.order import OrderItem
        count = db.session.query(OrderItem)\
            .join(ProductVariant, ProductVariant.id == OrderItem.product_variant_id)\
            .filter(ProductVariant.product_id == self.id)\
            .count()
        return count == 0

    def soft_delete(self):
        """Safely archive product so historical orders and reports remain valid."""
        self.status = 'ARCHIVED'
        db.session.commit()

    def __repr__(self):
        return f"<Product {self.id}: {self.name} ({self.status})>"


class ProductVariant(db.Model):
    __tablename__ = 'catalog_productvariant'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.BigInteger, db.ForeignKey('catalog_product.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    size_code = db.Column(db.String(10), default='STANDARD', nullable=False)
    sku = db.Column(db.String(60), unique=True, nullable=False, index=True)
    price = db.Column(db.Numeric(12, 2), nullable=False)
    sale_price = db.Column(db.Numeric(12, 2), nullable=True)
    stock = db.Column(db.Integer, default=10, nullable=False)
    low_stock_threshold = db.Column(db.Integer, default=3, nullable=False)
    is_default = db.Column(db.Boolean, default=False, nullable=False)

    @property
    def effective_price(self):
        if self.sale_price and self.sale_price > 0 and self.sale_price < self.price:
            return self.sale_price
        return self.price

    @property
    def is_on_sale(self):
        return bool(self.sale_price and self.sale_price > 0 and self.sale_price < self.price)

    @property
    def discount_percent(self):
        if self.is_on_sale and self.price and self.price > 0:
            pct = ((self.price - self.sale_price) / self.price) * 100
            return int(round(pct))
        return 0

    @property
    def is_low_stock(self):
        return self.stock <= self.low_stock_threshold

    def __repr__(self):
        return f"<ProductVariant {self.name} (SKU: {self.sku}, Stock: {self.stock})>"


class ProductImage(db.Model):
    __tablename__ = 'catalog_productimage'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.BigInteger, db.ForeignKey('catalog_product.id', ondelete='CASCADE'), nullable=False)
    image = db.Column(ImageColumn(200), nullable=False)
    alt_text = db.Column(db.String(200), default='', nullable=False)
    display_order = db.Column(db.Integer, default=0, nullable=False)

    @property
    def image_url(self):
        if not self.image:
            return '/static/images/placeholder-flower.jpg'
        if self.image.startswith('http') or self.image.startswith('/'):
            return self.image
        return f"/media/{self.image}"

    def __repr__(self):
        return f"<ProductImage {self.id} for Product {self.product_id}>"

