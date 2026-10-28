from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
from app.models.user import User

class LoginForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[Optional()])
    username_or_email = StringField('Tên đăng nhập hoặc Email', validators=[Optional()])
    password = PasswordField('Mật khẩu', validators=[DataRequired(message='Vui lòng nhập mật khẩu')])
    remember_me = BooleanField('Ghi nhớ đăng nhập')
    submit = SubmitField('Đăng Nhập')


class RegisterForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[
        DataRequired(message='Vui lòng nhập tên đăng nhập'),
        Length(min=3, max=50, message='Tên đăng nhập từ 3 đến 50 ký tự')
    ])
    email = StringField('Địa chỉ Email', validators=[
        DataRequired(message='Vui lòng nhập email'),
        Email(message='Email không đúng định dạng')
    ])
    first_name = StringField('Họ và tên đệm', validators=[DataRequired(message='Vui lòng nhập họ và tên')])
    last_name = StringField('Tên', validators=[DataRequired(message='Vui lòng nhập tên')])
    phone = StringField('Số điện thoại', validators=[
        DataRequired(message='Vui lòng nhập số điện thoại'),
        Length(min=9, max=15, message='Số điện thoại từ 9 đến 15 số')
    ])
    password = PasswordField('Mật khẩu', validators=[
        DataRequired(message='Vui lòng nhập mật khẩu'),
        Length(min=6, message='Mật khẩu tối thiểu 6 ký tự')
    ])
    confirm_password = PasswordField('Xác nhận mật khẩu', validators=[
        DataRequired(message='Vui lòng nhập lại mật khẩu'),
        EqualTo('password', message='Mật khẩu xác nhận không khớp')
    ])
    agree_terms = BooleanField('Tôi đồng ý với Điều khoản và Chính sách bán hàng', validators=[DataRequired(message='Bạn phải đồng ý với điều khoản')])
    submit = SubmitField('Đăng Ký Tài Khoản')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data.strip()).first():
            raise ValidationError('Tên đăng nhập này đã được sử dụng. Vui lòng chọn tên khác.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.strip().lower()).first():
            raise ValidationError('Địa chỉ email này đã được đăng ký. Vui lòng sử dụng email khác.')


class RequestResetForm(FlaskForm):
    email = StringField('Địa chỉ Email của bạn', validators=[
        DataRequired(message='Vui lòng nhập email'),
        Email(message='Email không hợp lệ')
    ])
    submit = SubmitField('Gửi Liên Kết Đặt Lại Mật Khẩu')

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data.strip().lower()).first()
        if not user:
            raise ValidationError('Không tìm thấy tài khoản nào gắn với địa chỉ email này.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Mật khẩu mới', validators=[
        DataRequired(message='Vui lòng nhập mật khẩu mới'),
        Length(min=6, message='Mật khẩu tối thiểu 6 ký tự')
    ])
    confirm_password = PasswordField('Xác nhận mật khẩu mới', validators=[
        DataRequired(message='Vui lòng xác nhận mật khẩu mới'),
        EqualTo('password', message='Mật khẩu xác nhận không khớp')
    ])
    submit = SubmitField('Cập Nhật Mật Khẩu')


class ProfileForm(FlaskForm):
    first_name = StringField('Họ và tên đệm', validators=[DataRequired()])
    last_name = StringField('Tên', validators=[DataRequired()])
    phone = StringField('Số điện thoại', validators=[DataRequired(), Length(min=9, max=15)])
    gender = SelectField('Giới tính', choices=[('M', 'Nam'), ('F', 'Nữ'), ('O', 'Khác')])
    date_of_birth = DateField('Ngày sinh', validators=[Optional()])
    submit = SubmitField('Lưu Thay Đổi')


class AddressForm(FlaskForm):
    full_name = StringField('Họ tên người nhận', validators=[DataRequired()])
    phone = StringField('Số điện thoại', validators=[DataRequired(), Length(min=9, max=15)])
    street_address = StringField('Địa chỉ (Số nhà, tên đường)', validators=[DataRequired()])
    ward = StringField('Phường/Xã', validators=[Optional()])
    district = StringField('Quận/Huyện', validators=[DataRequired()])
    city = StringField('Tỉnh/Thành phố', default='TP. Hồ Chí Minh', validators=[DataRequired()])
    is_default = BooleanField('Đặt làm địa chỉ mặc định')
    submit = SubmitField('Lưu Địa Chỉ')

