from datetime import date
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, DateField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError

TIME_SLOT_CHOICES = [
    ('08:00 - 10:00', 'Buổi sáng: 08:00 - 10:00'),
    ('10:00 - 12:00', 'Buổi trưa: 10:00 - 12:00'),
    ('13:30 - 15:30', 'Đầu giờ chiều: 13:30 - 15:30'),
    ('15:30 - 17:30', 'Cuối giờ chiều: 15:30 - 17:30'),
    ('18:00 - 20:00', 'Buổi tối: 18:00 - 20:00')
]

DISTRICT_CHOICES = [
    ('Quận 1', 'Quận 1'),
    ('Quận 3', 'Quận 3'),
    ('Quận 4', 'Quận 4'),
    ('Quận 5', 'Quận 5'),
    ('Quận 7', 'Quận 7'),
    ('Quận 10', 'Quận 10'),
    ('Quận Bình Thạnh', 'Quận Bình Thạnh'),
    ('Quận Phú Nhuận', 'Quận Phú Nhuận'),
    ('Thành phố Thủ Đức', 'Thành phố Thủ Đức'),
    ('Quận Tân Bình', 'Quận Tân Bình'),
    ('Quận Gò Vấp', 'Quận Gò Vấp')
]

class CheckoutForm(FlaskForm):
    # Sender details
    sender_name = StringField('Họ và tên người đặt', validators=[DataRequired(message='Vui lòng nhập họ tên người đặt')])
    sender_phone = StringField('Số điện thoại liên hệ', validators=[
        DataRequired(message='Vui lòng nhập số điện thoại'),
        Length(min=9, max=15, message='Số điện thoại từ 9 đến 15 số')
    ])
    sender_email = StringField('Email nhận thông báo đơn', validators=[
        DataRequired(message='Vui lòng nhập email'),
        Email(message='Email không hợp lệ')
    ])

    # Delivery & Recipient
    delivery_method = StringField('Phương thức nhận hoa', default='DELIVERY')
    recipient_name = StringField('Họ và tên người nhận hoa', validators=[Optional()])
    recipient_phone = StringField('Số điện thoại người nhận', validators=[Optional()])
    delivery_address = StringField('Địa chỉ giao hoa (Số nhà, tên đường)', validators=[Optional()])
    delivery_ward = StringField('Phường/Xã', validators=[Optional()])
    delivery_district = StringField('Quận/Huyện', validators=[Optional()])
    delivery_city = StringField('Tỉnh/Thành phố', default='TP. Hồ Chí Minh', validators=[Optional()])
    delivery_date = DateField('Ngày giao hoa mong muốn', validators=[DataRequired(message='Vui lòng chọn ngày giao')], default=date.today)
    delivery_time_slot = StringField('Khung giờ giao hoa', validators=[DataRequired(message='Vui lòng chọn khung giờ giao')])

    # Card & greeting message
    card_message = TextAreaField('Nội dung in trên thiệp/băng rôn', validators=[Optional(), Length(max=500)])
    card_sender_name = StringField('Tên ký trên thiệp', validators=[Optional(), Length(max=120)])
    is_anonymous = BooleanField('Gửi hoa ẩn danh (Không ghi tên người gửi cho người nhận)')

    # Notes & Payment
    customer_notes = TextAreaField('Ghi chú giao hàng cho shipper', validators=[Optional()])
    payment_method = StringField('Hình thức thanh toán', default='BANK_TRANSFER')

    submit = SubmitField('Xác Nhận Đặt Hàng')

    def validate_delivery_date(self, field):
        if field.data and field.data < date.today():
            raise ValidationError('Ngày giao hoa không thể ở trong quá khứ.')


class OrderCancelForm(FlaskForm):
    cancellation_reason = TextAreaField('Lý do yêu cầu hủy đơn', validators=[
        DataRequired(message='Vui lòng cung cấp lý do hủy đơn'),
        Length(min=5, max=500, message='Lý do từ 5 đến 500 ký tự')
    ])
    submit = SubmitField('Xác Nhận Hủy Đơn Hàng')

