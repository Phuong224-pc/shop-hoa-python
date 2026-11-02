from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Optional

class AiAskForm(FlaskForm):
    query = StringField('Câu hỏi', validators=[DataRequired(message='Vui lòng nhập câu hỏi'), Length(max=1500)])

class AiSearchForm(FlaskForm):
    q = StringField('Từ khóa tìm kiếm thông minh', validators=[DataRequired(), Length(max=300)])
    min_price = DecimalField('Giá tối thiểu', validators=[Optional()])
    max_price = DecimalField('Giá tối đa', validators=[Optional()])
    in_stock = BooleanField('Chỉ xem mẫu còn hàng', default=False)

