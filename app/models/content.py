from datetime import datetime
from app.extensions import db
from app.models.fields import ImageColumn

class Banner(db.Model):
    __tablename__ = 'content_banner'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    subtitle = db.Column(db.String(255), default='', nullable=False)
    badge = db.Column(db.String(50), default='', nullable=False)
    link = db.Column(db.String(200), default='/products', nullable=False)
    button_text = db.Column(db.String(50), default='Khám phá ngay', nullable=False)
    image = db.Column(ImageColumn(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    display_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @property
    def image_url(self):
        if not self.image:
            return '/static/images/hero-banner.jpg'
        if self.image.startswith('http') or self.image.startswith('/'):
            return self.image
        return f"/media/{self.image}"

    def __repr__(self):
        return f"<Banner {self.title}>"


class ContactMessage(db.Model):
    __tablename__ = 'content_contactmessage'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(254), nullable=False)
    phone = db.Column(db.String(20), default='', nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(15), default='NEW', nullable=False)  # NEW, PROCESSING, RESOLVED, SPAM
    internal_notes = db.Column(db.Text, default='', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('auth_user.id'), nullable=True)

    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id])

    def __repr__(self):
        return f"<ContactMessage #{self.id} from {self.full_name}>"


class FAQ(db.Model):
    __tablename__ = 'content_faq'

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), default='Chung', nullable=False)
    display_order = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<FAQ {self.question}>"


class PageContent(db.Model):
    __tablename__ = 'content_pagecontent'

    id = db.Column(db.Integer, primary_key=True)
    page_type = db.Column(db.String(30), unique=True, nullable=False)  # ABOUT, POLICY, TERMS, CARE_GUIDE
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, default='', nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<PageContent {self.page_type}: {self.title}>"

