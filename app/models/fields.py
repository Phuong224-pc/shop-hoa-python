from app.extensions import db

class MediaImage(str):
    """
    A string subclass representing an image path that provides a .url property,
    ensuring 100% compatibility with templates expecting Django-style ImageField attributes.
    """
    @property
    def url(self):
        if not self:
            return '/static/images/placeholder-flower.jpg'
        val = str(self)
        if val.startswith('http://') or val.startswith('https://') or val.startswith('/'):
            return val
        return f"/media/{val}"


class ImageColumn(db.TypeDecorator):
    """
    SQLAlchemy column type that transparently wraps image path strings into MediaImage objects.
    """
    impl = db.String
    cache_ok = True

    def process_result_value(self, value, dialect):
        if value is None or value == '':
            return None
        return MediaImage(value)

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(value)

