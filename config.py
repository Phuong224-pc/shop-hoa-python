import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'flora-flower-secret-key-super-secure-change-in-production-2026')
    db_env = os.environ.get('DATABASE_URL', '').strip()
    if db_env:
        if db_env.startswith('sqlite:///') and not db_env.startswith('sqlite:////') and not (len(db_env) > 11 and db_env[10] == ':'):
            rel_file = db_env.replace('sqlite:///', '')
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{(BASE_DIR / rel_file).as_posix()}"
        else:
            SQLALCHEMY_DATABASE_URI = db_env
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{(BASE_DIR / 'db.sqlite3').as_posix()}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Uploads / Media
    MEDIA_FOLDER = BASE_DIR / 'media'
    UPLOAD_FOLDER = BASE_DIR / 'media'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max

    # Flask-WTF CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    # Flask-Mail Settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get(
        'MAIL_DEFAULT_SENDER',
        'Flora Flower Boutique <noreply@floraflower.vn>'
    )

    # Shop Owner Notification Email (Strict requirement from specification)
    SHOP_NOTIFICATION_EMAIL = os.environ.get(
        'SHOP_NOTIFICATION_EMAIL',
        'phuongtruong121204@gmail.com'
    )

    # Public Base URL for email verification and password reset links
    PUBLIC_BASE_URL = os.environ.get('PUBLIC_BASE_URL', 'http://127.0.0.1:5000')

    # Pagination
    ITEMS_PER_PAGE = 12

    # AI & Gemini Configuration
    AI_MODE = os.environ.get('AI_MODE', 'gemini').lower()  # gemini, demo, mock
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-3.5-flash-lite')
    GEMINI_EMBED_MODEL = os.environ.get('GEMINI_EMBED_MODEL', 'gemini-embedding-001')
    AI_REQUEST_TIMEOUT = int(os.environ.get('AI_REQUEST_TIMEOUT', 30))
    AI_RATE_LIMIT_PER_MINUTE = int(os.environ.get('AI_RATE_LIMIT_PER_MINUTE', 20))

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    AI_MODE = 'mock'
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'TEST_DATABASE_URL',
        f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
    )
    MAIL_SUPPRESS_SEND = True
    SERVER_NAME = 'localhost.localdomain'

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
