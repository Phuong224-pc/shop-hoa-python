import os
from decimal import Decimal
from datetime import datetime
from flask import Flask, send_from_directory, render_template, request, session
from markupsafe import Markup
from config import config_by_name, BASE_DIR
from app.extensions import db, migrate, login_manager, mail, csrf
from app.models.core import ShopSetting
from app.models.catalog import Category
from app.services.cart import get_current_cart

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')

    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / 'templates'),
        static_folder=str(BASE_DIR / 'static'),
        static_url_path='/static'
    )

    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    # Media / Uploaded files serving
    @app.route('/media/<path:filename>')
    def media_files(filename):
        return send_from_directory(app.config['MEDIA_FOLDER'], filename)

    # Custom Jinja Filters
    def format_currency(value):
        if value is None or value == '':
            return "0 đ"
        try:
            val = int(Decimal(str(value)))
            return f"{val:,}".replace(",", ".") + " đ"
        except Exception:
            return f"{value} đ"

    def format_date(value, fmt='%d/%m/%Y'):
        if not value:
            return ''
        if isinstance(value, str):
            try:
                value = datetime.strptime(value[:10], '%Y-%m-%d')
            except Exception:
                return value
        # Handle format strings like 'Y-m-d' or 'd/m/Y H:i'
        clean_fmt = fmt.replace('Y', '%Y').replace('m', '%m').replace('d', '%d').replace('H', '%H').replace('i', '%M')
        if not '%' in clean_fmt:
            clean_fmt = '%d/%m/%Y'
        try:
            return value.strftime(clean_fmt)
        except Exception:
            return str(value)

    def order_status_badge(status):
        badges = {
            'PENDING': '<span class="badge bg-warning text-dark"><i class="bi bi-clock me-1"></i> Chờ xác nhận</span>',
            'CONFIRMED': '<span class="badge bg-info text-dark"><i class="bi bi-check-circle me-1"></i> Đã xác nhận</span>',
            'PREPARING': '<span class="badge bg-primary"><i class="bi bi-flower1 me-1"></i> Đang chuẩn bị hoa</span>',
            'READY': '<span class="badge bg-indigo text-white" style="background-color: #6366F1;"><i class="bi bi-box-seam me-1"></i> Sẵn sàng giao</span>',
            'DELIVERING': '<span class="badge bg-info text-white"><i class="bi bi-truck me-1"></i> Đang giao hoa</span>',
            'COMPLETED': '<span class="badge bg-success"><i class="bi bi-check2-all me-1"></i> Hoàn tất</span>',
            'CANCELLED': '<span class="badge bg-danger"><i class="bi bi-x-circle me-1"></i> Đã hủy</span>'
        }
        return Markup(badges.get(status, f'<span class="badge bg-secondary">{status}</span>'))

    def payment_status_badge(status):
        badges = {
            'PENDING': '<span class="badge bg-secondary">Chưa thanh toán</span>',
            'WAITING_VERIFICATION': '<span class="badge bg-warning text-dark">Chờ đối soát biên lai</span>',
            'PAID': '<span class="badge bg-success">Đã thanh toán</span>',
            'FAILED': '<span class="badge bg-danger">Thanh toán thất bại</span>',
            'REFUNDED': '<span class="badge bg-dark">Đã hoàn tiền</span>'
        }
        return Markup(badges.get(status, f'<span class="badge bg-secondary">{status}</span>'))

    app.jinja_env.filters['currency'] = format_currency
    app.jinja_env.filters['date'] = format_date
    app.jinja_env.filters['order_status_badge'] = order_status_badge
    app.jinja_env.filters['payment_status_badge'] = payment_status_badge

    # Register compatibility extension and filters for template compatibility
    from app.jinja_compat import register_filters_and_extensions
    register_filters_and_extensions(app)

    class ResolverMatchCompat:
        def __init__(self, endpoint):
            self.endpoint = endpoint or ''
            parts = self.endpoint.split('.')
            self.url_name = 'home' if self.endpoint in ['main.index', 'index'] else (parts[-1] if parts else '')
            self.namespace = parts[0] if len(parts) > 1 else ''

        def __str__(self):
            return self.url_name

        def __eq__(self, other):
            return self.url_name == other or self.endpoint == other

    @app.before_request
    def attach_request_compat():
        request.GET = request.args
        request.POST = request.form
        request.resolver_match = ResolverMatchCompat(request.endpoint)

    # Jinja Global helpers
    @app.context_processor
    def inject_globals():
        if not hasattr(request, 'resolver_match'):
            request.resolver_match = ResolverMatchCompat(getattr(request, 'endpoint', ''))
        try:
            shop_setting = ShopSetting.get_settings()
        except Exception:
            shop_setting = None

        try:
            header_categories = Category.query.filter_by(is_active=True).order_by(Category.display_order.asc()).all()
        except Exception:
            header_categories = []

        from flask_login import current_user
        try:
            cart = get_current_cart(current_user)
            cart_item_count = cart.total_items_count if cart else 0
        except Exception:
            cart = None
            cart_item_count = 0

        from app.models.promotion import Coupon
        from app.models.catalog import Occasion
        try:
            active_coupons = Coupon.query.filter_by(is_active=True).all()
        except Exception:
            active_coupons = []

        try:
            occasions = Occasion.query.filter_by(is_active=True).order_by(Occasion.display_order.asc()).all()
        except Exception:
            occasions = []

        from flask import get_flashed_messages
        flashed = get_flashed_messages(with_categories=True)
        class FlashMsg(str):
            pass
        msg_list = []
        for cat, txt in flashed:
            m = FlashMsg(txt)
            m.tags = cat
            msg_list.append(m)

        profile = getattr(current_user, 'profile', None) if getattr(current_user, 'is_authenticated', False) else None

        return dict(
            messages=msg_list,
            user=current_user,
            current_user=current_user,
            profile=profile,
            shop_setting=shop_setting,
            setting=shop_setting,
            header_categories=header_categories,
            nav_categories=header_categories,
            categories=header_categories,
            occasions=occasions,
            nav_occasions=occasions,
            global_cart=cart,
            cart=cart,
            cart_item_count=cart_item_count,
            active_coupons=active_coupons,
            now=datetime.now()
        )

    # Register Blueprints
    from app.blueprints.main import bp as main_bp
    from app.blueprints.auth import bp as auth_bp
    from app.blueprints.catalog import bp as catalog_bp
    from app.blueprints.cart import bp as cart_bp
    from app.blueprints.orders import bp as orders_bp
    from app.blueprints.reviews import bp as reviews_bp
    from app.blueprints.dashboard import bp as dashboard_bp
    from app.blueprints.api import bp as api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(catalog_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp)

    # Exclude REST API from CSRF protection for programmatic access
    csrf.exempt(api_bp)

    # Error handlers
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    return app
