from decimal import Decimal
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DecimalField, IntegerField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, ValidationError
from app.models.catalog import Product

class ProductForm(FlaskForm):
    name = StringField('Tên mẫu hoa', validators=[
        DataRequired(message='Vui lòng nhập tên mẫu hoa'),
        Length(max=200, message='Tối đa 200 ký tự')
    ])
    sku = StringField('Mã sản phẩm (SKU)', validators=[
        DataRequired(message='Vui lòng nhập mã SKU'),
        Length(max=50, message='Tối đa 50 ký tự')
    ])
    primary_category_id = SelectField('Danh mục chính', coerce=int, validators=[DataRequired(message='Vui lòng chọn danh mục')])
    presentation_style = SelectField('Kiểu dáng hoa', choices=[
        ('BOUQUET', 'Bó hoa tươi'),
        ('BASKET', 'Giỏ hoa'),
        ('VASE', 'Bình hoa / Lọ hoa'),
        ('BOX', 'Hộp hoa'),
        ('STAND', 'Kệ hoa chúc mừng / khai trương')
    ], default='BOUQUET')
    color_tone = SelectField('Tông màu chủ đạo', choices=[
        ('RED', 'Đỏ lãng mạn'),
        ('PINK', 'Hồng dịu dàng'),
        ('WHITE', 'Trắng tinh khôi'),
        ('YELLOW', 'Vàng rực rỡ'),
        ('PURPLE', 'Tím thơ mộng'),
        ('PASTEL', 'Pastel nhẹ nhàng'),
        ('MIXED', 'Đa sắc phối hợp')
    ], default='MIXED')
    short_description = StringField('Mô tả ngắn', validators=[
        DataRequired(message='Vui lòng nhập mô tả ngắn'),
        Length(max=300, message='Tối đa 300 ký tự')
    ])
    description = TextAreaField('Mô tả chi tiết', validators=[DataRequired(message='Vui lòng nhập mô tả chi tiết')])
    flower_composition = StringField('Thành phần các loài hoa', validators=[Optional(), Length(max=350)])
    care_instructions = TextAreaField('Hướng dẫn chăm sóc hoa tươi', validators=[Optional()])
    seasonal_policy_notes = TextAreaField('Lưu ý hoa theo mùa / thay thế hoa phụ', validators=[Optional()])
    status = SelectField('Trạng thái hiển thị', choices=[
        ('PUBLISHED', 'Đang bán (Công khai)'),
        ('DRAFT', 'Bản nháp (Tạm ẩn)'),
        ('ARCHIVED', 'Lưu trữ (Đã ngừng kinh doanh)')
    ], default='PUBLISHED')
    is_featured = BooleanField('Sản phẩm nổi bật (Hiển thị trang chủ)')
    is_bestseller_manual = BooleanField('Gắn nhãn Bán chạy (Bestseller)')
    main_image = FileField('Ảnh đại diện sản phẩm', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Chỉ chấp nhận file ảnh JPG, JPEG, PNG, WEBP')
    ])

    # Variant fields for rapid product creation
    default_variant_name = StringField('Tên phiên bản mặc định', default='Tiêu chuẩn (Standard)', validators=[Optional()])
    default_price = DecimalField('Giá bán (VNĐ)', default=Decimal('650000.00'), validators=[
        Optional(),
        NumberRange(min=0, message='Giá không được âm')
    ])
    default_sale_price = DecimalField('Giá ưu đãi/khuyến mãi (VNĐ)', validators=[
        Optional(),
        NumberRange(min=0, message='Giá ưu đãi không được âm')
    ])
    default_stock = IntegerField('Số lượng tồn kho ban đầu', default=15, validators=[
        Optional(),
        NumberRange(min=0, message='Tồn kho không được âm')
    ])

    submit = SubmitField('Lưu Mẫu Hoa')

    def __init__(self, original_sku=None, is_create=False, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.original_sku = original_sku
        self.is_create = is_create

    def validate_sku(self, field):
        sku = (field.data or '').strip().upper()
        if self.original_sku and sku == self.original_sku:
            return
        if Product.query.filter_by(sku=sku).first():
            raise ValidationError('Mã SKU này đã tồn tại trong hệ thống. Vui lòng đặt mã khác.')

    def validate_default_price(self, field):
        if self.is_create and (field.data is None or field.data < 0):
            raise ValidationError('Vui lòng nhập giá bán cho biến thể mặc định.')

    def validate_default_stock(self, field):
        if self.is_create and (field.data is None or field.data < 0):
            raise ValidationError('Vui lòng nhập số lượng tồn kho ban đầu.')


class VariantForm(FlaskForm):
    name = StringField('Tên biến thể / Kích cỡ', validators=[DataRequired(), Length(max=100)])
    size_code = SelectField('Mã kích thước', choices=[
        ('STANDARD', 'Tiêu chuẩn (Standard)'),
        ('DELUXE', 'Cao cấp (Deluxe)'),
        ('PREMIUM', 'Đặc biệt (Premium)'),
        ('VIP', 'Sang trọng (VIP)')
    ], default='STANDARD')
    sku = StringField('Mã SKU biến thể', validators=[DataRequired(), Length(max=60)])
    price = DecimalField('Giá bán (VNĐ)', validators=[DataRequired(), NumberRange(min=0)])
    sale_price = DecimalField('Giá khuyến mãi (VNĐ)', validators=[Optional(), NumberRange(min=0)])
    stock = IntegerField('Tồn kho', validators=[DataRequired(), NumberRange(min=0)])
    low_stock_threshold = IntegerField('Ngưỡng báo động sắp hết', default=3, validators=[DataRequired(), NumberRange(min=0)])
    is_default = BooleanField('Phiên bản mặc định')
    submit = SubmitField('Lưu Biến Thể')


class CategoryForm(FlaskForm):
    name = StringField('Tên danh mục', validators=[DataRequired(), Length(max=100)])
    slug = StringField('Đường dẫn (Slug)', validators=[Optional(), Length(max=120)])
    description = TextAreaField('Mô tả danh mục', validators=[Optional()])
    icon = StringField('Icon Bootstrap', default='bi-flower1', validators=[DataRequired()])
    image = FileField('Ảnh đại diện danh mục', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Chỉ chấp nhận file ảnh')
    ])
    is_active = BooleanField('Kích hoạt hiển thị', default=True)
    display_order = IntegerField('Thứ tự sắp xếp', default=0, validators=[Optional()])
    submit = SubmitField('Lưu Danh Mục')


class SearchForm(FlaskForm):
    class Meta:
        csrf = False  # GET request form doesn't need CSRF token

    q = StringField('Từ khóa tìm kiếm')
    category = StringField('Danh mục')
    occasion = StringField('Dịp tặng')
    sort = SelectField('Sắp xếp theo', choices=[
        ('newest', 'Mới nhất'),
        ('price_asc', 'Giá tăng dần'),
        ('price_desc', 'Giá giảm dần'),
        ('bestseller', 'Bán chạy nhất')
    ], default='newest')
    min_price = DecimalField('Giá tối thiểu', validators=[Optional()])
    max_price = DecimalField('Giá tối đa', validators=[Optional()])

