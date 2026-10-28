from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.extensions import db
from app.models.catalog import Product, Category, Occasion
from app.models.content import Banner, FAQ, PageContent, ContactMessage
from app.models.core import ShopSetting

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    banners = Banner.query.filter_by(is_active=True).order_by(Banner.display_order.asc()).all()
    categories = Category.query.filter_by(is_active=True).order_by(Category.display_order.asc()).all()
    occasions = Occasion.query.filter_by(is_active=True).order_by(Occasion.display_order.asc()).all()
    featured_products = Product.query.filter_by(status='PUBLISHED', is_featured=True).limit(8).all()
    bestsellers = Product.query.filter_by(status='PUBLISHED', is_bestseller_manual=True).limit(4).all()
    if not bestsellers:
        bestsellers = Product.query.filter_by(status='PUBLISHED').order_by(Product.created_at.desc()).limit(4).all()

    return render_template(
        'shop/index.html',
        banners=banners,
        categories=categories,
        occasions=occasions,
        featured_products=featured_products,
        bestsellers=bestsellers,
        bestseller_products=bestsellers
    )


@bp.route('/about')
def about():
    page = PageContent.query.filter_by(page_type='ABOUT').first()
    return render_template('shop/about.html', page=page)


@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()

        if not full_name or not email or not subject or not message:
            flash('Vui lòng điền đầy đủ các trường thông tin bắt buộc.', 'danger')
        else:
            msg = ContactMessage(
                full_name=full_name,
                email=email,
                phone=phone,
                subject=subject,
                message=message,
                status='NEW'
            )
            db.session.add(msg)
            db.session.commit()
            flash('Tin nhắn của bạn đã được gửi thành công! Flora Flower sẽ phản hồi trong thời gian sớm nhất.', 'success')
            return redirect(url_for('main.contact'))

    faqs = FAQ.query.filter_by(is_active=True).order_by(FAQ.display_order.asc()).all()
    return render_template('shop/contact.html', faqs=faqs)


@bp.route('/policy')
def policy():
    policy_type = request.args.get('page_type', 'POLICY')
    policy_content = PageContent.query.filter_by(page_type=policy_type).first()
    if not policy_content:
        policy_content = PageContent.query.first()
    if not policy_content:
        policy_content = PageContent(
            page_type='POLICY',
            title='Chính Sách & Hỗ Trợ Khách Hàng',
            content='Flora Flower cam kết cung cấp hoa tươi chất lượng cao với dịch vụ giao hàng chu đáo, đúng giờ.'
        )
    return render_template('shop/policy.html', page=policy_content, policy=policy_content)
