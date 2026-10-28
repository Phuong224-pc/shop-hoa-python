from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
# Add Django-compatible .pk property to all SQLAlchemy models
db.Model.pk = property(lambda self: getattr(self, 'id', None))
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Vui lòng đăng nhập để tiếp tục truy cập.'
login_manager.login_message_category = 'warning'

