from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class ReviewForm(FlaskForm):
    rating = SelectField('Đánh giá chất lượng', choices=[
        ('5', '5 Sao - Tuyệt vời, hoa rất tươi và đẹp'),
        ('4', '4 Sao - Hài lòng, đúng mẫu'),
        ('3', '3 Sao - Bình thường'),
        ('2', '2 Sao - Cần cải thiện'),
        ('1', '1 Sao - Không hài lòng')
    ], default='5')
    comment = TextAreaField('Cảm nhận của bạn về bó hoa', validators=[
        DataRequired(message='Vui lòng chia sẻ cảm nhận của bạn'),
        Length(min=5, max=1000, message='Đánh giá từ 5 đến 1000 ký tự')
    ])
    submit = SubmitField('Gửi Đánh Giá')

