import os
import csv
import io
from datetime import datetime, date, timedelta
from decimal import Decimal
from werkzeug.utils import secure_filename
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, abort, Response, current_app
)
from flask_login import login_required, current_user
from app.extensions import db
from app.models.catalog import (
    Product, ProductVariant, Category, Occasion,
    ProductImage, Accessory
)
from app.models.order import Order, OrderItem, OrderStatusHistory
from app.models.payment import PaymentTransaction
from app.models.inventory import StockTransaction
from app.models.review import ProductReview
from app.models.user import User, UserProfile
from app.models.content import Banner, ContactMessage, FAQ, PageContent
from app.models.core import ShopSetting, AuditLog
from app.models.promotion import Coupon
from app.forms.catalog import ProductForm, VariantForm, CategoryForm

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.before_request
def verify_staff_access():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login', next=request.path))
    if not current_user.is_store_staff():
        abort(403)


class PageObjCompat:
    def __init__(self, p):
        self.p = p
        self.has_other_pages = p.pages > 1
        self.has_previous = p.has_prev
        self.previous_page_number = p.prev_num or 1
        self.has_next = p.has_next
        self.next_page_number = p.next_num or p.pages
        self.number = p.page
        self.paginator = type('Paginator', (), {
            'page_range': list(range(1, p.pages + 1))
        })()

    def __iter__(self):
        return iter(self.p.items)

    def __len__(self):
        return len(self.p.items)

# -------------------------------------------------------------
# 1. OVERVIEW & ANALYTICS
# -------------------------------------------------------------
@bp.route('/')
def overview():
    range_filter = request.args.get('range', '30d')
    today = date.today()

    if range_filter == 'today':
        start_date = today
        end_date = today
    elif range_filter == '7d':
        start_date = today - timedelta(days=7)
        end_date = today
    elif range_filter == 'this_month':
        start_date = today.replace(day=1)
        end_date = today
    elif range_filter == 'custom':
        start_str = request.args.get('start_date')
        end_str = request.args.get('end_date')
        try:
            start_date = datetime.strptime(start_str, '%Y-%m-%d').date() if start_str else today - timedelta(days=30)
            end_date = datetime.strptime(end_str, '%Y-%m-%d').date() if end_str else today
        except ValueError:
            start_date = today - timedelta(days=30)
            end_date = today
    else:  # 30d default
        start_date = today - timedelta(days=30)
        end_date = today

    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())

    # Completed orders in range
    completed_orders = Order.query.filter(
        Order.status == 'COMPLETED',
        Order.created_at >= start_dt,
        Order.created_at <= end_dt
    ).all()

    sales_revenue = sum(o.total_amount for o in completed_orders)

    # Net money collected (PAID transactions minus refunds)
    paid_txs = PaymentTransaction.query.filter(
        PaymentTransaction.status == 'PAID',
        PaymentTransaction.created_at >= start_dt,
        PaymentTransaction.created_at <= end_dt
    ).all()
    net_money_collected = sum(tx.amount for tx in paid_txs)

    all_orders_in_range = Order.query.filter(
        Order.created_at >= start_dt,
        Order.created_at <= end_dt
    ).all()
    total_orders_count = len(all_orders_in_range)
    orders_completed_count = len(completed_orders)
    orders_cancelled_count = sum(1 for o in all_orders_in_range if o.status == 'CANCELLED')
    aov = (sales_revenue / orders_completed_count) if orders_completed_count > 0 else Decimal('0.00')

    # Operational metrics
    today_orders_count = Order.query.filter(
        Order.delivery_date == today,
        Order.status.in_(['CONFIRMED', 'PREPARING', 'READY', 'DELIVERING'])
    ).count()

    waiting_transfers_count = PaymentTransaction.query.filter_by(
        payment_method='BANK_TRANSFER',
        status='WAITING_VERIFICATION'
    ).count()

    low_stock_variants_count = ProductVariant.query.filter(
        ProductVariant.stock <= ProductVariant.low_stock_threshold
    ).count()

    # Sold items and unique buyers
    total_items_sold = sum(
        sum(item.quantity for item in o.items) for o in completed_orders
    )
    unique_buyers_count = len(set(o.user_id for o in completed_orders))

    # Order status counts (All time)
    status_counts = {
        'PENDING': Order.query.filter_by(status='PENDING').count(),
        'CONFIRMED': Order.query.filter_by(status='CONFIRMED').count(),
        'PREPARING': Order.query.filter_by(status='PREPARING').count(),
        'READY': Order.query.filter_by(status='READY').count(),
        'DELIVERING': Order.query.filter_by(status='DELIVERING').count(),
        'COMPLETED': Order.query.filter_by(status='COMPLETED').count(),
        'CANCELLED': Order.query.filter_by(status='CANCELLED').count(),
    }

    # Revenue trend data by day
    date_rev_map = {}
    curr = start_date
    while curr <= end_date:
        date_rev_map[curr.strftime('%d/%m')] = 0
        curr += timedelta(days=1)

    for o in completed_orders:
        d_str = o.created_at.strftime('%d/%m')
        if d_str in date_rev_map:
            date_rev_map[d_str] += int(o.total_amount)

    chart_dates = list(date_rev_map.keys())
    chart_revenue = list(date_rev_map.values())

    # Category revenue
    cat_rev_map = {}
    for cat in Category.query.all():
        cat_rev_map[cat.name] = 0

    for o in completed_orders:
        for item in o.items:
            if item.variant and item.variant.product and item.variant.product.primary_category:
                cname = item.variant.product.primary_category.name
                cat_rev_map[cname] = cat_rev_map.get(cname, 0) + int(item.subtotal)

    chart_cat_labels = list(cat_rev_map.keys())
    chart_cat_data = list(cat_rev_map.values())

    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(8).all()

    # Top 5 products
    top_products = []
    prod_sales = {}
    for o in completed_orders:
        for item in o.items:
            pname = item.product_name
            if pname not in prod_sales:
                prod_sales[pname] = {'product_name': pname, 'sold_qty': 0, 'total_sales': Decimal('0.00')}
            prod_sales[pname]['sold_qty'] += item.quantity
            prod_sales[pname]['total_sales'] += item.subtotal

    top_products = sorted(prod_sales.values(), key=lambda x: x['sold_qty'], reverse=True)[:5]

    return render_template(
        'dashboard/index.html',
        range_filter=range_filter,
        start_date=start_date,
        end_date=end_date,
        sales_revenue=sales_revenue,
        net_money_collected=net_money_collected,
        total_orders_count=total_orders_count,
        orders_completed_count=orders_completed_count,
        orders_cancelled_count=orders_cancelled_count,
        aov=aov,
        today_orders_count=today_orders_count,
        waiting_transfers_count=waiting_transfers_count,
        low_stock_variants_count=low_stock_variants_count,
        total_items_sold=total_items_sold,
        unique_buyers_count=unique_buyers_count,
        orders_pending_count=status_counts['PENDING'],
        orders_confirmed_count=status_counts['CONFIRMED'],
        orders_preparing_count=status_counts['PREPARING'],
        orders_ready_count=status_counts['READY'],
        orders_delivering_count=status_counts['DELIVERING'],
        chart_dates=chart_dates,
        chart_revenue=chart_revenue,
        chart_cat_labels=chart_cat_labels,
        chart_cat_data=chart_cat_data,
        recent_orders=recent_orders,
        top_products=top_products
    )


# -------------------------------------------------------------
# 2. PRODUCT CRUD & SAFE DELETION
# -------------------------------------------------------------
@bp.route('/products')
def product_list():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '').strip()
    category_id = request.args.get('category_id', type=int)
    status = request.args.get('status', '').strip()

    query = Product.query

    if q:
        query = query.filter((Product.name.ilike(f"%{q}%")) | (Product.sku.ilike(f"%{q}%")))
    if category_id:
        query = query.filter_by(primary_category_id=category_id)
    if status:
        query = query.filter_by(status=status)

    pagination = query.order_by(Product.created_at.desc()).paginate(page=page, per_page=15, error_out=False)
    categories = Category.query.order_by(Category.name.asc()).all()

    return render_template(
        'dashboard/products/list.html',
        products=pagination.items,
        pagination=pagination,
        page_obj=PageObjCompat(pagination),
        categories=categories,
        q=q,
        selected_cat=category_id,
        selected_status=status
    )


@bp.route('/products/create', methods=['GET', 'POST'])
def product_create():
    form = ProductForm()
    form.primary_category_id.choices = [(c.id, c.name) for c in Category.query.filter_by(is_active=True).all()]

    if form.validate_on_submit():
        import re
        slug = re.sub(r'[^\w\s-]', '', form.name.data.strip().lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        # Ensure unique slug
        if Product.query.filter_by(slug=slug).first():
            slug = f"{slug}-{int(datetime.utcnow().timestamp())}"

        # Handle image upload
        image_path = ''
        if form.main_image.data:
            f = form.main_image.data
            fname = secure_filename(f.filename)
            upload_dir = current_app.config['MEDIA_FOLDER'] / 'products'
            upload_dir.mkdir(parents=True, exist_ok=True)
            saved_name = f"product_{int(datetime.utcnow().timestamp())}_{fname}"
            f.save(upload_dir / saved_name)
            image_path = f"products/{saved_name}"

        product = Product(
            name=form.name.data.strip(),
            slug=slug,
            sku=form.sku.data.strip().upper(),
            main_image=image_path,
            primary_category_id=form.primary_category_id.data,
            presentation_style=form.presentation_style.data,
            color_tone=form.color_tone.data,
            short_description=form.short_description.data.strip(),
            description=form.description.data.strip(),
            flower_composition=form.flower_composition.data.strip() if form.flower_composition.data else '',
            care_instructions=form.care_instructions.data.strip() if form.care_instructions.data else '',
            seasonal_policy_notes=form.seasonal_policy_notes.data.strip() if form.seasonal_policy_notes.data else '',
            status=form.status.data,
            is_featured=form.is_featured.data,
            is_bestseller_manual=form.is_bestseller_manual.data
        )
        db.session.add(product)
        db.session.flush()

        # Create initial default variant
        variant = ProductVariant(
            product_id=product.id,
            name=form.default_variant_name.data.strip(),
            size_code='STANDARD',
            sku=f"{product.sku}-STD",
            price=form.default_price.data,
            sale_price=form.default_sale_price.data if form.default_sale_price.data else None,
            stock=form.default_stock.data,
            is_default=True
        )
        db.session.add(variant)

        AuditLog.log(current_user, 'CREATE', 'Product', product.id, product.name, f"Tạo mẫu hoa mới SKU={product.sku}")
        db.session.commit()

        flash(f'Mẫu hoa "{product.name}" đã được tạo thành công!', 'success')
        return redirect(url_for('dashboard.product_list'))

    return render_template('dashboard/products/form.html', form=form, title='Thêm Mẫu Hoa Mới')


@bp.route('/products/<int:id>/edit', methods=['GET', 'POST'])
def product_edit(id):
    product = Product.query.get_or_404(id)
    form = ProductForm(original_sku=product.sku, obj=product)
    form.primary_category_id.choices = [(c.id, c.name) for c in Category.query.filter_by(is_active=True).all()]

    default_v = product.default_variant

    if request.method == 'GET':
        if default_v:
            form.default_variant_name.data = default_v.name
            form.default_price.data = default_v.price
            form.default_sale_price.data = default_v.sale_price
            form.default_stock.data = default_v.stock

    if form.validate_on_submit():
        product.name = form.name.data.strip()
        product.sku = form.sku.data.strip().upper()
        product.primary_category_id = form.primary_category_id.data
        product.presentation_style = form.presentation_style.data
        product.color_tone = form.color_tone.data
        product.short_description = form.short_description.data.strip()
        product.description = form.description.data.strip()
        product.flower_composition = form.flower_composition.data.strip() if form.flower_composition.data else ''
        product.care_instructions = form.care_instructions.data.strip() if form.care_instructions.data else ''
        product.seasonal_policy_notes = form.seasonal_policy_notes.data.strip() if form.seasonal_policy_notes.data else ''
        product.status = form.status.data
        product.is_featured = form.is_featured.data
        product.is_bestseller_manual = form.is_bestseller_manual.data

        if form.main_image.data:
            f = form.main_image.data
            fname = secure_filename(f.filename)
            upload_dir = current_app.config['MEDIA_FOLDER'] / 'products'
            upload_dir.mkdir(parents=True, exist_ok=True)
            saved_name = f"product_{int(datetime.utcnow().timestamp())}_{fname}"
            f.save(upload_dir / saved_name)
            product.main_image = f"products/{saved_name}"

        if default_v:
            default_v.name = form.default_variant_name.data.strip()
            default_v.price = form.default_price.data
            default_v.sale_price = form.default_sale_price.data if form.default_sale_price.data else None
            default_v.stock = form.default_stock.data

        AuditLog.log(current_user, 'UPDATE', 'Product', product.id, product.name, f"Cập nhật thông tin mẫu hoa #{product.id}")
        db.session.commit()

        flash(f'Cập nhật mẫu hoa "{product.name}" thành công!', 'success')
        return redirect(url_for('dashboard.product_list'))

    variants = product.variants.all()
    gallery_images = product.gallery_images.all()
    variant_form = VariantForm()

    return render_template(
        'dashboard/products/form.html',
        form=form,
        product=product,
        variants=variants,
        gallery_images=gallery_images,
        variant_form=variant_form,
        title=f'Chỉnh Sửa Mẫu Hoa: {product.name}'
    )


@bp.route('/products/<int:id>/delete', methods=['POST'])
def product_delete(id):
    """
    Implements Safe Deletion / Soft Delete:
    - If the product has past order transactions, it MUST NOT be hard-deleted,
      as this would break historical customer receipts and revenue accounting.
      Instead, it is safely soft-deleted (status = 'ARCHIVED').
    - If no order references exist, it is cleanly removed.
    """
    product = Product.query.get_or_404(id)

    if not product.can_be_hard_deleted():
        product.soft_delete()
        AuditLog.log(
            current_user, 'DELETE', 'Product', product.id, product.name,
            "Thực hiện Xóa Mềm (ARCHIVED) do sản phẩm đã có đơn hàng trong lịch sử."
        )
        flash(
            f'Sản phẩm "{product.name}" đã được chuyển sang chế độ LƯU TRỮ (Xóa mềm - ARCHIVED) '
            f'vì đã có khách đặt hàng trong lịch sử. Lịch sử hóa đơn và báo cáo doanh thu được bảo toàn tuyệt đối.',
            'warning'
        )
    else:
        name = product.name
        db.session.delete(product)
        AuditLog.log(current_user, 'DELETE', 'Product', id, name, "Xóa hoàn toàn sản phẩm khỏi hệ thống (chưa có đơn hàng).")
        db.session.commit()
        flash(f'Đã xóa hoàn toàn mẫu hoa "{name}" khỏi hệ thống.', 'success')

    return redirect(url_for('dashboard.product_list'))


@bp.route('/products/<int:id>/toggle-status', methods=['POST'])
def product_toggle_status(id):
    """Đổi trạng thái hiển thị nhanh của sản phẩm (PUBLISHED, HIDDEN, ARCHIVED, DRAFT)."""
    product = Product.query.get_or_404(id)
    new_status = request.form.get('status')
    if new_status in ['PUBLISHED', 'HIDDEN', 'ARCHIVED', 'DRAFT']:
        old_status = product.status
        product.status = new_status
        AuditLog.log(current_user, 'UPDATE', 'Product', product.id, product.name, f"Đổi trạng thái sản phẩm từ {old_status} sang {new_status}")
        db.session.commit()
        flash(f'Đã cập nhật trạng thái mẫu hoa "{product.name}" sang {new_status}.', 'success')
    return redirect(url_for('dashboard.product_list'))


# -------------------------------------------------------------
# 3. CATEGORIES & ACCESSORIES
# -------------------------------------------------------------
@bp.route('/categories', methods=['GET', 'POST'])
def categories():
    form = CategoryForm()
    if form.validate_on_submit():
        import re
        slug = form.slug.data.strip() if form.slug.data else form.name.data.strip().lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)

        cat = Category(
            name=form.name.data.strip(),
            slug=slug,
            description=form.description.data.strip() if form.description.data else '',
            icon=form.icon.data.strip(),
            is_active=form.is_active.data,
            display_order=form.display_order.data or 0
        )
        db.session.add(cat)
        db.session.commit()
        flash('Đã thêm danh mục mới thành công.', 'success')
        return redirect(url_for('dashboard.categories'))

    all_cats = Category.query.order_by(Category.display_order.asc(), Category.name.asc()).all()
    return render_template('dashboard/products/categories.html', categories=all_cats, form=form)


@bp.route('/accessories', methods=['GET', 'POST'])
def accessories():
    from app.models.catalog import Accessory
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        price = Decimal(request.form.get('price', '0'))
        stock = int(request.form.get('stock', '0'))
        acc_id = request.form.get('id')
        if acc_id:
            acc = Accessory.query.get_or_404(int(acc_id))
            acc.name = name
            acc.price = price
            acc.stock = stock
            acc.is_active = bool(request.form.get('is_active'))
            flash(f'Đã cập nhật phụ kiện "{name}".', 'success')
        else:
            acc = Accessory(name=name, price=price, stock=stock, is_active=True)
            db.session.add(acc)
            flash(f'Đã thêm phụ kiện mới "{name}".', 'success')
        db.session.commit()
        return redirect(url_for('dashboard.accessories'))

    all_acc = Accessory.query.order_by(Accessory.id.desc()).all()
    return render_template('dashboard/products/accessories.html', accessories=all_acc)


# -------------------------------------------------------------
# 4. ORDERS & DELIVERIES
# -------------------------------------------------------------
@bp.route('/orders')
def order_list():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '').strip()
    q = request.args.get('q', '').strip()

    query = Order.query
    if status:
        query = query.filter_by(status=status)
    if q:
        query = query.filter(
            (Order.order_number.ilike(f"%{q}%")) |
            (Order.sender_name.ilike(f"%{q}%")) |
            (Order.sender_phone.ilike(f"%{q}%")) |
            (Order.recipient_name.ilike(f"%{q}%")) |
            (Order.recipient_phone.ilike(f"%{q}%"))
        )

    pagination = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=15, error_out=False)
    return render_template(
        'dashboard/orders/list.html',
        orders=pagination.items,
        pagination=pagination,
        page_obj=PageObjCompat(pagination),
        selected_status=status,
        q=q
    )


@bp.route('/orders/<int:id>', methods=['GET', 'POST'])
def order_detail(id):
    order = Order.query.get_or_404(id)
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'update_notes':
            order.internal_notes = request.form.get('internal_notes', '').strip()
            db.session.commit()
            AuditLog.log(current_user, 'UPDATE', 'Order', order.id, f"#{order.order_number}", "Cập nhật ghi chú nội bộ")
            flash('Đã cập nhật ghi chú nội bộ cho đơn hàng thành công!', 'success')
            return redirect(url_for('dashboard.order_detail', id=id))

        new_status = request.form.get('status')
        note = request.form.get('note', '').strip()
        valid_statuses = [s[0] for s in Order.STATUS_CHOICES]
        if new_status in valid_statuses and new_status != order.status:
            old_status = order.status
            order.status = new_status
            if new_status == 'COMPLETED':
                order.completed_at = datetime.utcnow()
            elif new_status == 'CANCELLED':
                order.cancelled_at = datetime.utcnow()
                order.cancelled_by_id = current_user.id
                order.cancellation_reason = note
                from app.services.inventory import record_order_cancellation
                record_order_cancellation(order, performed_by=current_user, reason=note)

            history = OrderStatusHistory(
                order_id=order.id,
                from_status=old_status,
                to_status=new_status,
                note=note or f"Chuyển trạng thái từ {old_status} sang {new_status}",
                changed_by_id=current_user.id
            )
            db.session.add(history)
            AuditLog.log(current_user, 'UPDATE', 'Order', order.id, f"#{order.order_number}", f"Trạng thái: {old_status} -> {new_status}")
            db.session.commit()
            flash(f'Đã cập nhật trạng thái đơn hàng sang: {order.get_status_display}', 'success')
        return redirect(url_for('dashboard.order_detail', id=id))

    setting = ShopSetting.get_settings()
    payment = order.payment
    return render_template(
        'dashboard/orders/detail.html',
        order=order,
        statuses=Order.STATUS_CHOICES,
        payment=payment,
        setting=setting
    )


@bp.route('/orders/<int:id>/status', methods=['POST'])
def order_update_status(id):
    order = Order.query.get_or_404(id)
    new_status = request.form.get('status')
    note = request.form.get('note', '').strip()

    valid_statuses = ['PENDING', 'CONFIRMED', 'PREPARING', 'READY', 'DELIVERING', 'COMPLETED', 'CANCELLED']
    if new_status in valid_statuses and new_status != order.status:
        old_status = order.status
        order.status = new_status
        if new_status == 'COMPLETED':
            order.completed_at = datetime.utcnow()
        elif new_status == 'CANCELLED':
            order.cancelled_at = datetime.utcnow()
            order.cancelled_by_id = current_user.id
            order.cancellation_reason = note
            from app.services.inventory import record_order_cancellation
            record_order_cancellation(order, performed_by=current_user, reason=note)

        history = OrderStatusHistory(
            order_id=order.id,
            from_status=old_status,
            to_status=new_status,
            note=note or f"Chuyển trạng thái từ {old_status} sang {new_status}",
            changed_by_id=current_user.id
        )
        db.session.add(history)
        AuditLog.log(current_user, 'UPDATE', 'Order', order.id, f"#{order.order_number}", f"Trạng thái: {old_status} -> {new_status}")
        db.session.commit()
        flash(f'Đã cập nhật trạng thái đơn hàng sang: {new_status}', 'success')

    return redirect(url_for('dashboard.order_detail', id=id))


@bp.route('/orders/<int:id>/print-bill')
def print_bill(id):
    order = Order.query.get_or_404(id)
    shop_setting = ShopSetting.get_settings()
    return render_template('dashboard/orders/print_bill.html', order=order, shop_setting=shop_setting)


@bp.route('/orders/<int:id>/print-florist')
def print_florist(id):
    order = Order.query.get_or_404(id)
    return render_template('dashboard/orders/print_florist.html', order=order)


@bp.route('/orders/calendar')
def delivery_calendar():
    target_str = request.args.get('date')
    today = date.today()
    try:
        target_date = datetime.strptime(target_str, '%Y-%m-%d').date() if target_str else today
    except ValueError:
        target_date = today

    # 7 week days
    week_days = []
    monday = target_date - timedelta(days=target_date.weekday())
    day_labels = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ Nhật']
    for i in range(7):
        d = monday + timedelta(days=i)
        count = Order.query.filter(
            Order.delivery_date == d,
            Order.status.in_(['CONFIRMED', 'PREPARING', 'READY', 'DELIVERING'])
        ).count()
        week_days.append({
            'date': d,
            'label': f"{day_labels[i]} ({d.strftime('%d/%m')})",
            'is_selected': d == target_date,
            'count': count
        })

    day_orders = Order.query.filter(
        Order.delivery_date == target_date,
        Order.status.in_(['CONFIRMED', 'PREPARING', 'READY', 'DELIVERING', 'COMPLETED'])
    ).all()

    slots_config = [
        ('08:00 - 10:00', 'Buổi sáng: 08:00 - 10:00'),
        ('10:00 - 12:00', 'Buổi trưa: 10:00 - 12:00'),
        ('13:30 - 15:30', 'Đầu giờ chiều: 13:30 - 15:30'),
        ('15:30 - 17:30', 'Cuối giờ chiều: 15:30 - 17:30'),
        ('18:00 - 20:00', 'Buổi tối: 18:00 - 20:00')
    ]

    slots_data = {}
    for code, label in slots_config:
        matching = [o for o in day_orders if o.delivery_time_slot == code]
        slots_data[code] = {
            'label': label,
            'orders': matching
        }

    return render_template(
        'dashboard/orders/calendar.html',
        target_date=target_date,
        week_days=week_days,
        total_orders_today=len(day_orders),
        slots_data=slots_data
    )


# -------------------------------------------------------------
# 5. INVENTORY & STOCK
# -------------------------------------------------------------
@bp.route('/inventory')
def inventory_list():
    page = request.args.get('page', 1, type=int)
    low_stock = request.args.get('low_stock')
    q = request.args.get('q', '').strip()

    query = ProductVariant.query.join(Product)
    if low_stock == '1':
        query = query.filter(ProductVariant.stock <= ProductVariant.low_stock_threshold)
    if q:
        query = query.filter(
            (Product.name.ilike(f"%{q}%")) |
            (ProductVariant.name.ilike(f"%{q}%")) |
            (ProductVariant.sku.ilike(f"%{q}%"))
        )

    pagination = query.order_by(ProductVariant.stock.asc()).paginate(page=page, per_page=15, error_out=False)
    recent_transactions = StockTransaction.query.order_by(StockTransaction.created_at.desc()).limit(15).all()

    return render_template(
        'dashboard/inventory/list.html',
        variants=pagination.items,
        page_obj=PageObjCompat(pagination),
        pagination=pagination,
        current_low_stock=low_stock,
        current_q=q,
        recent_transactions=recent_transactions
    )


@bp.route('/inventory/import/<int:id>', methods=['POST'])
def inventory_import(id):
    variant = ProductVariant.query.get_or_404(id)
    quantity = request.form.get('quantity', type=int)
    reason = request.form.get('reason', '').strip()

    if quantity and quantity > 0:
        old_stock = variant.stock
        new_stock = old_stock + quantity
        variant.stock = new_stock

        txn = StockTransaction(
            variant_id=variant.id,
            transaction_type='IMPORT',
            quantity_change=quantity,
            balance_after=new_stock,
            reason=reason or 'Nhập thêm hoa tươi vào kho',
            performed_by_id=current_user.id
        )
        db.session.add(txn)
        AuditLog.log(current_user, 'IMPORT', 'Inventory', variant.id, variant.sku, f"Nhập kho +{quantity}: {old_stock} -> {new_stock}")
        db.session.commit()
        flash(f'Đã nhập thêm {quantity} sản phẩm cho biến thể {variant.sku} thành công!', 'success')

    return redirect(url_for('dashboard.inventory_list'))


@bp.route('/inventory/adjust/<int:id>', methods=['POST'])
def inventory_adjust(id):
    variant = ProductVariant.query.get_or_404(id)
    new_stock = request.form.get('new_stock', type=int)
    reason = request.form.get('reason', '').strip()

    if new_stock is not None and new_stock >= 0:
        old_stock = variant.stock
        diff = new_stock - old_stock
        variant.stock = new_stock

        txn = StockTransaction(
            variant_id=variant.id,
            transaction_type='ADJUSTMENT',
            quantity_change=diff,
            balance_after=new_stock,
            reason=reason or 'Điều chỉnh tồn kho bởi quản lý',
            performed_by_id=current_user.id
        )
        db.session.add(txn)
        AuditLog.log(current_user, 'UPDATE', 'Inventory', variant.id, variant.sku, f"Điều chỉnh tồn kho: {old_stock} -> {new_stock}")
        db.session.commit()
        flash(f'Đã cập nhật số lượng tồn kho biến thể {variant.sku} thành công!', 'success')

    return redirect(url_for('dashboard.inventory_list'))


# -------------------------------------------------------------
# 6. PAYMENTS & VERIFICATION
# -------------------------------------------------------------
@bp.route('/payments', methods=['GET', 'POST'])
def payment_list():
    if request.method == 'POST':
        payment_id = request.form.get('payment_id') or request.args.get('id')
        if payment_id:
            return payment_verify(int(payment_id))

    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '').strip()
    query = PaymentTransaction.query
    if status:
        query = query.filter_by(status=status)

    pagination = query.order_by(PaymentTransaction.created_at.desc()).paginate(page=page, per_page=15, error_out=False)
    waiting_count = PaymentTransaction.query.filter_by(
        payment_method='BANK_TRANSFER',
        status='WAITING_VERIFICATION'
    ).count()

    return render_template(
        'dashboard/payments/list.html',
        transactions=pagination.items,
        pagination=pagination,
        page_obj=PageObjCompat(pagination),
        current_status=status,
        selected_status=status,
        waiting_count=waiting_count
    )


@bp.route('/payments/<int:id>/verify', methods=['POST'])
def payment_verify(id):
    tx = PaymentTransaction.query.get_or_404(id)
    action = request.form.get('action')  # approve, reject, cod_confirm

    if action in ['approve', 'cod_confirm']:
        tx.status = 'PAID'
        tx.verified_at = datetime.utcnow()
        tx.verified_by_id = current_user.id
        if tx.order and tx.order.status in ['PENDING', 'CONFIRMED']:
            tx.order.status = 'CONFIRMED'
        AuditLog.log(current_user, 'UPDATE', 'Payment', tx.id, tx.transaction_code, "Xác nhận đối soát thanh toán thành công (PAID).")
        flash(f'Đã xác nhận thanh toán đơn hàng #{tx.order.order_number if tx.order else tx.id} thành công.', 'success')
    elif action == 'reject':
        tx.status = 'FAILED'
        tx.rejection_reason = request.form.get('reason', 'Giao dịch không hợp lệ').strip()
        AuditLog.log(current_user, 'UPDATE', 'Payment', tx.id, tx.transaction_code, f"Từ chối thanh toán: {tx.rejection_reason}")
        flash('Đã từ chối giao dịch thanh toán.', 'warning')

    db.session.commit()
    return redirect(url_for('dashboard.payment_list'))


@bp.route('/payments/<int:id>/proof')
def view_proof(id):
    tx = PaymentTransaction.query.get_or_404(id)
    if not tx.proof_image:
        flash('Giao dịch chưa có ảnh biên lai chuyển khoản.', 'warning')
        return redirect(url_for('dashboard.payment_list'))

    from flask import send_from_directory
    file_path = os.path.join(current_app.config['MEDIA_FOLDER'], tx.proof_image)
    if not os.path.exists(file_path):
        flash('Tệp ảnh biên lai không tồn tại trên hệ thống.', 'danger')
        return redirect(url_for('dashboard.payment_list'))

    dirname, filename = os.path.split(file_path)
    return send_from_directory(dirname, filename)


@bp.route('/payments/<int:id>/refund', methods=['POST'])
def payment_refund(id):
    tx = PaymentTransaction.query.get_or_404(id)
    amount = Decimal(request.form.get('amount', str(tx.amount)))
    reason = request.form.get('reason', '').strip()
    refund_code = request.form.get('refund_transaction_code', '').strip()

    from app.models.payment import RefundRecord
    refund = RefundRecord(
        payment_id=tx.id,
        amount=amount,
        reason=reason,
        refund_transaction_code=refund_code,
        processed_by_id=current_user.id
    )
    db.session.add(refund)
    tx.status = 'REFUNDED'
    if tx.order:
        tx.order.status = 'CANCELLED'
        tx.order.cancellation_reason = f"Đã hoàn tiền: {reason}"
    AuditLog.log(current_user, 'UPDATE', 'Payment', tx.id, tx.transaction_code, f"Hoàn tiền {amount}: {reason}")
    db.session.commit()
    flash(f'Đã ghi nhận hoàn tiền {amount:,.0f} đ cho đơn hàng.', 'success')
    return redirect(url_for('dashboard.payment_list'))


# -------------------------------------------------------------
# 7. REVIEWS MODERATION
# -------------------------------------------------------------
@bp.route('/reviews')
def review_list():
    reviews = ProductReview.query.order_by(ProductReview.created_at.desc()).all()
    return render_template('dashboard/reviews/list.html', reviews=reviews)


@bp.route('/reviews/<int:id>/moderate', methods=['POST'])
@bp.route('/reviews/<int:id>/status', methods=['POST'])
def review_moderate(id):
    rev = ProductReview.query.get_or_404(id)
    action = request.form.get('action') or request.form.get('status')
    if action in ['approve', 'APPROVED']:
        rev.status = 'APPROVED'
        rev.is_approved = True
        flash('Đã duyệt hiển thị đánh giá của khách hàng.', 'success')
    elif action in ['hide', 'reject', 'REJECTED', 'HIDDEN']:
        rev.status = 'HIDDEN'
        rev.is_approved = False
        flash('Đã ẩn đánh giá.', 'info')
    db.session.commit()
    return redirect(url_for('dashboard.review_list'))


# -------------------------------------------------------------
# 8. CUSTOMERS & STAFF
# -------------------------------------------------------------
@bp.route('/customers')
def customer_list():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '').strip()

    query = User.query.filter_by(is_staff=False, is_superuser=False)
    if q:
        query = query.filter(
            (User.username.ilike(f"%{q}%")) |
            (User.email.ilike(f"%{q}%")) |
            (User.first_name.ilike(f"%{q}%")) |
            (User.last_name.ilike(f"%{q}%"))
        )

    pagination = query.order_by(User.date_joined.desc()).paginate(page=page, per_page=15, error_out=False)

    for c in pagination.items:
        c.orders_count = c.orders.count()
        completed_orders = c.orders.filter(Order.status.in_(['COMPLETED', 'CONFIRMED', 'DELIVERING', 'PREPARING', 'READY'])).all()
        c.total_spent = sum(o.total_amount for o in completed_orders)

    return render_template(
        'dashboard/customers/list.html',
        customers=pagination.items,
        page_obj=PageObjCompat(pagination),
        pagination=pagination,
        total_count=pagination.total,
        current_q=q
    )


@bp.route('/customers/<int:id>')
def customer_detail(id):
    customer = User.query.get_or_404(id)
    orders = customer.orders.order_by(Order.created_at.desc()).all()
    total_spent = sum(o.total_amount for o in orders if o.status in ['COMPLETED', 'CONFIRMED', 'DELIVERING'])
    return render_template(
        'dashboard/customers/detail.html',
        customer=customer,
        orders=orders,
        total_spent=total_spent
    )


@bp.route('/customers/<int:id>/toggle-lock', methods=['POST'])
def customer_toggle_lock(id):
    customer = User.query.get_or_404(id)
    if not customer.profile:
        customer.profile = UserProfile(user_id=customer.id)
        db.session.add(customer.profile)
    customer.profile.is_locked = not customer.profile.is_locked
    status_text = "ĐÃ KHÓA" if customer.profile.is_locked else "ĐÃ MỞ KHÓA"
    AuditLog.log(current_user, 'STATUS_CHANGE', 'User', customer.id, customer.username, f"{status_text} tài khoản {customer.username}")
    db.session.commit()
    flash(f'{status_text} tài khoản khách hàng {customer.username}.', 'success')
    return redirect(url_for('dashboard.customer_detail', id=customer.id))


@bp.route('/staff')
def staff_list():
    if not current_user.is_admin():
        abort(403)
    staff = User.query.filter((User.is_staff == True) | (User.is_superuser == True)).all()
    return render_template('dashboard/staff/list.html', staff=staff)


# -------------------------------------------------------------
# 9. PROMOTIONS & COUPONS
# -------------------------------------------------------------
@bp.route('/promotions')
def promotion_list():
    coupons = Coupon.query.order_by(Coupon.id.desc()).all()
    return render_template('dashboard/promotions/list.html', coupons=coupons)


@bp.route('/promotions/save', methods=['POST'])
def promotion_save():
    code = request.form.get('code', '').strip().upper()
    title = request.form.get('title', '').strip()
    discount_type = request.form.get('discount_type', 'PERCENT')
    dtype = 'PERCENTAGE' if discount_type in ['PERCENT', 'PERCENTAGE'] else 'FIXED_AMOUNT'
    discount_value = Decimal(request.form.get('discount_value', '0'))
    max_discount_raw = request.form.get('max_discount_amount', '').strip()
    max_discount_amount = Decimal(max_discount_raw) if max_discount_raw else None
    min_order_amount = Decimal(request.form.get('min_order_amount', '0') or '0')

    valid_from_raw = request.form.get('valid_from', '').strip()
    valid_to_raw = request.form.get('valid_to', '').strip()
    valid_from = datetime.strptime(valid_from_raw, '%Y-%m-%d') if valid_from_raw else datetime.utcnow()
    valid_to = datetime.strptime(valid_to_raw, '%Y-%m-%d') if valid_to_raw else datetime.utcnow()

    usage_limit = int(request.form.get('usage_limit', '100') or 100)
    is_active = bool(request.form.get('is_active'))

    coupon = Coupon.query.filter_by(code=code).first()
    if coupon:
        coupon.title = title
        coupon.discount_type = dtype
        coupon.discount_value = discount_value
        coupon.max_discount_amount = max_discount_amount
        coupon.min_order_amount = min_order_amount
        coupon.valid_from = valid_from
        coupon.valid_to = valid_to
        coupon.usage_limit = usage_limit
        coupon.is_active = is_active
        flash(f'Đã cập nhật mã giảm giá {code}.', 'success')
        AuditLog.log(current_user, 'UPDATE', 'Coupon', coupon.id, coupon.code, f"Cập nhật mã giảm giá {code}")
    else:
        coupon = Coupon(
            code=code,
            title=title,
            discount_type=dtype,
            discount_value=discount_value,
            max_discount_amount=max_discount_amount,
            min_order_amount=min_order_amount,
            valid_from=valid_from,
            valid_to=valid_to,
            usage_limit=usage_limit,
            is_active=is_active
        )
        db.session.add(coupon)
        flash(f'Đã tạo mã giảm giá mới {code} thành công!', 'success')
        AuditLog.log(current_user, 'CREATE', 'Coupon', 0, code, f"Tạo mã giảm giá mới {code}")

    db.session.commit()
    return redirect(url_for('dashboard.promotion_list'))


# -------------------------------------------------------------
# 10. CONTACT MESSAGES
# -------------------------------------------------------------
@bp.route('/contacts')
def contact_message_list():
    messages_qs = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('dashboard/content/contacts.html', messages_qs=messages_qs)


@bp.route('/contacts/<int:id>/update', methods=['POST'])
def contact_message_update(id):
    msg = ContactMessage.query.get_or_404(id)
    new_status = request.form.get('status', 'NEW')
    if new_status in ['NEW', 'PROCESSING', 'RESOLVED', 'SPAM']:
        msg.status = new_status
        msg.assigned_to_id = current_user.id
        db.session.commit()
        AuditLog.log(current_user, 'UPDATE', 'ContactMessage', msg.id, msg.full_name, f"Cập nhật trạng thái tin nhắn #{msg.id} sang {new_status}")
        flash('Đã cập nhật trạng thái tin nhắn liên hệ thành công!', 'success')
    return redirect(url_for('dashboard.contact_message_list'))


# -------------------------------------------------------------
# 9. SETTINGS & LOGS & CSV EXPORT
# -------------------------------------------------------------
@bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if not current_user.is_admin():
        abort(403)
    setting = ShopSetting.get_settings()
    if request.method == 'POST':
        setting.shop_name = request.form.get('shop_name', '').strip()
        setting.phone = request.form.get('phone', '').strip()
        setting.hotline = request.form.get('hotline', '').strip()
        setting.email = request.form.get('email', '').strip()
        setting.address = request.form.get('address', '').strip()
        setting.bank_code = request.form.get('bank_code', '').strip()
        setting.bank_name = request.form.get('bank_name', '').strip()
        setting.bank_account_no = request.form.get('bank_account_no', '').strip()
        setting.bank_account_name = request.form.get('bank_account_name', '').strip()
        db.session.commit()
        flash('Cập nhật cấu hình cửa hàng thành công!', 'success')
        return redirect(url_for('dashboard.settings'))

    return render_template('dashboard/settings/index.html', setting=setting)


@bp.route('/logs')
def logs():
    page = request.args.get('page', 1, type=int)
    pagination = AuditLog.query.order_by(AuditLog.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template(
        'dashboard/logs/list.html',
        logs=pagination.items,
        pagination=pagination,
        page_obj=PageObjCompat(pagination)
    )


@bp.route('/export-csv')
def export_csv():
    target = request.args.get('target', 'orders')
    output = io.StringIO()
    writer = csv.writer(output)

    if target == 'orders':
        writer.writerow(['Order Number', 'Date', 'Sender', 'Recipient', 'Phone', 'Total Amount', 'Status', 'Payment'])
        orders = Order.query.order_by(Order.created_at.desc()).all()
        for o in orders:
            writer.writerow([
                o.order_number,
                o.created_at.strftime('%Y-%m-%d %H:%M'),
                o.sender_name,
                o.recipient_name,
                o.recipient_phone,
                float(o.total_amount),
                o.status,
                o.payment_status
            ])
        filename = f"orders_export_{date.today().strftime('%Y%m%d')}.csv"
    else:
        writer.writerow(['SKU', 'Product Name', 'Variant', 'Price', 'Sale Price', 'Stock'])
        variants = ProductVariant.query.join(Product).all()
        for v in variants:
            writer.writerow([
                v.sku,
                v.product.name,
                v.name,
                float(v.price),
                float(v.sale_price) if v.sale_price else '',
                v.stock
            ])
        filename = f"inventory_export_{date.today().strftime('%Y%m%d')}.csv"

    AuditLog.log(current_user, 'EXPORT', 'CSV', 0, filename, f"Xuất báo cáo CSV mục {target}")
    return Response(
        output.getvalue().encode('utf-8-sig'),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )
