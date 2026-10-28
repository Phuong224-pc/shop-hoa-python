import uuid
from datetime import datetime, date
from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.order import Order, OrderItem, OrderItemAccessory, OrderStatusHistory
from app.models.payment import PaymentTransaction
from app.models.core import ShopSetting
from app.forms.order import CheckoutForm, OrderCancelForm
from app.services.cart import get_current_cart
from app.services.inventory import record_order_sale, record_order_cancellation
from app.services.email import send_order_confirmation_to_customer, send_new_order_notification_to_shop_owner

bp = Blueprint('orders', __name__, url_prefix='/orders')

@bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    # Business rule: staff/admin cannot order as a customer
    if current_user.is_store_staff():
        flash('Tài khoản Quản trị / Nhân viên không thể thực hiện đặt hoa qua giao diện khách hàng. Vui lòng đăng nhập tài khoản Khách hàng (ví dụ: khachhang1 / customer123).', 'warning')
        return redirect(url_for('dashboard.overview'))

    cart = get_current_cart(current_user)
    if cart.total_items_count == 0:
        flash('Giỏ hàng của bạn đang trống. Vui lòng chọn hoa trước khi thanh toán.', 'warning')
        return redirect(url_for('catalog.product_list'))

    shop_setting = ShopSetting.get_settings()
    user_addresses = current_user.addresses.all() if hasattr(current_user, 'addresses') else []
    default_address = current_user.addresses.filter_by(is_default=True).first() if hasattr(current_user, 'addresses') else None
    if not default_address and user_addresses:
        default_address = user_addresses[0]

    min_date_str = date.today().strftime('%Y-%m-%d')
    time_slots = Order.TIME_SLOT_CHOICES

    form = CheckoutForm()

    # Pre-fill form on GET
    if request.method == 'GET':
        form.sender_name.data = current_user.full_name
        form.sender_email.data = current_user.email
        if current_user.profile and current_user.profile.phone:
            form.sender_phone.data = current_user.profile.phone
        if default_address:
            form.recipient_name.data = default_address.full_name
            form.recipient_phone.data = default_address.phone
            form.delivery_address.data = default_address.street_address
            form.delivery_ward.data = default_address.ward
            form.delivery_district.data = default_address.district
            form.delivery_city.data = default_address.city

    if form.validate_on_submit():
        delivery_method = form.delivery_method.data or 'DELIVERY'
        recipient_name = form.recipient_name.data.strip() if form.recipient_name.data else ''
        recipient_phone = form.recipient_phone.data.strip() if form.recipient_phone.data else ''
        delivery_address = form.delivery_address.data.strip() if form.delivery_address.data else ''

        if delivery_method == 'DELIVERY':
            if not (recipient_name and recipient_phone and delivery_address):
                flash('Vui lòng điền đầy đủ họ tên, số điện thoại và địa chỉ của người nhận hoa.', 'danger')
                return render_template(
                    'shop/checkout.html',
                    form=form,
                    cart=cart,
                    shop_setting=shop_setting,
                    setting=shop_setting,
                    user_addresses=user_addresses,
                    default_address=default_address,
                    min_date_str=min_date_str,
                    time_slots=time_slots
                )
        else:
            if not recipient_name:
                recipient_name = form.sender_name.data.strip()
            if not recipient_phone:
                recipient_phone = form.sender_phone.data.strip()
            if not delivery_address:
                delivery_address = f"Nhận trực tiếp tại Cửa hàng: {shop_setting.address}"

        # Cut-off time validation
        delivery_date = form.delivery_date.data
        now = datetime.now()
        if delivery_date == date.today():
            if now.hour >= shop_setting.same_day_cutoff_hour:
                flash(f'Cửa hàng đã ngừng nhận đơn giao trong ngày hôm nay sau {shop_setting.same_day_cutoff_hour}:00. Vui lòng chọn ngày giao từ ngày mai.', 'warning')
                return render_template(
                    'shop/checkout.html',
                    form=form,
                    cart=cart,
                    shop_setting=shop_setting,
                    setting=shop_setting,
                    user_addresses=user_addresses,
                    default_address=default_address,
                    min_date_str=min_date_str,
                    time_slots=time_slots
                )

        # Stock check
        for c_item in cart.items.all():
            variant = c_item.variant
            if variant and variant.stock < c_item.quantity:
                flash(f"Mẫu hoa '{variant.product.name} ({variant.name})' chỉ còn {variant.stock} sản phẩm trong kho.", 'danger')
                return redirect(url_for('cart.view_cart'))

        flowers_subtotal = cart.flowers_subtotal
        accessories_subtotal = cart.accessories_subtotal
        discount_amount = cart.discount_amount

        # Shipping fee
        if delivery_method == 'PICKUP' or (flowers_subtotal + accessories_subtotal) >= shop_setting.free_shipping_threshold:
            shipping_fee = Decimal('0.00')
        else:
            shipping_fee = shop_setting.shipping_fee_default

        total_amount = max(Decimal('0.00'), (flowers_subtotal + accessories_subtotal + shipping_fee) - discount_amount)
        order_number = f"FF{datetime.utcnow().strftime('%y%m%d%H%M')}{uuid.uuid4().hex[:4].upper()}"

        order = Order(
            order_number=order_number,
            status='PENDING',
            delivery_method=delivery_method,
            sender_name=form.sender_name.data.strip(),
            sender_phone=form.sender_phone.data.strip(),
            sender_email=form.sender_email.data.strip().lower(),
            recipient_name=recipient_name,
            recipient_phone=recipient_phone,
            delivery_address=delivery_address,
            delivery_ward=form.delivery_ward.data.strip() if form.delivery_ward.data else '',
            delivery_district=form.delivery_district.data.strip() if form.delivery_district.data else '',
            delivery_city=form.delivery_city.data.strip() if form.delivery_city.data else 'TP. Hồ Chí Minh',
            delivery_date=delivery_date,
            delivery_time_slot=form.delivery_time_slot.data,
            card_message=form.card_message.data.strip() if form.card_message.data else '',
            card_sender_name=form.card_sender_name.data.strip() if form.card_sender_name.data else '',
            is_anonymous=form.is_anonymous.data,
            customer_notes=form.customer_notes.data.strip() if form.customer_notes.data else '',
            flowers_subtotal=flowers_subtotal,
            accessories_subtotal=accessories_subtotal,
            shipping_fee=shipping_fee,
            discount_amount=discount_amount,
            total_amount=total_amount,
            coupon_code_snapshot=cart.coupon.code if cart.coupon else '',
            coupon_id=cart.coupon_id,
            user_id=current_user.id
        )
        db.session.add(order)
        db.session.flush()

        # Create Order Items from Cart Items
        for c_item in cart.items.all():
            o_item = OrderItem(
                order_id=order.id,
                product_variant_id=c_item.variant_id,
                product_name=c_item.variant.product.name if c_item.variant else 'Mẫu hoa',
                variant_name=c_item.variant.name if c_item.variant else 'Tiêu chuẩn',
                sku=c_item.variant.sku if c_item.variant else '',
                unit_price=c_item.variant.effective_price if c_item.variant else Decimal('0.00'),
                quantity=c_item.quantity,
                subtotal=Decimal(str(c_item.variant.effective_price)) * c_item.quantity
            )
            db.session.add(o_item)
            db.session.flush()

            # Accessories for item
            for c_acc in c_item.accessories.all():
                o_acc = OrderItemAccessory(
                    order_item_id=o_item.id,
                    accessory_id=c_acc.accessory_id,
                    accessory_name=c_acc.accessory.name if c_acc.accessory else 'Phụ kiện',
                    unit_price=c_acc.accessory.price if c_acc.accessory else Decimal('0.00'),
                    quantity=c_acc.quantity,
                    subtotal=Decimal(str(c_acc.accessory.price)) * c_acc.quantity
                )
                db.session.add(o_acc)

        # Payment Transaction
        payment_method = form.payment_method.data or 'BANK_TRANSFER'
        initial_status = 'WAITING_VERIFICATION' if payment_method == 'BANK_TRANSFER' else 'PENDING'
        tx = PaymentTransaction(
            order_id=order.id,
            payment_method=payment_method,
            status=initial_status,
            amount=total_amount,
            transaction_code=f"TX-{order_number}"
        )
        db.session.add(tx)

        # Order status history
        history = OrderStatusHistory(
            order_id=order.id,
            from_status='NONE',
            to_status='PENDING',
            note='Đơn hàng được đặt thành công bởi khách hàng',
            changed_by_id=current_user.id
        )
        db.session.add(history)

        # Update coupon used count if any
        if cart.coupon:
            cart.coupon.used_count += 1

        # Decrement stock and audit
        record_order_sale(order)

        # Clear cart
        cart.clear()
        db.session.commit()

        # Send Emails via Flask-Mail
        try:
            # 1. Customer confirmation email
            send_order_confirmation_to_customer(order)
            # 2. Shop owner alert to phuongtruong121204@gmail.com
            send_new_order_notification_to_shop_owner(order)
        except Exception:
            pass

        flash(f'Đặt hoa thành công! Mã đơn hàng của bạn là #{order.order_number}.', 'success')
        return redirect(url_for('orders.order_success', order_number=order.order_number))

    return render_template(
        'shop/checkout.html',
        form=form,
        cart=cart,
        shop_setting=shop_setting,
        setting=shop_setting,
        user_addresses=user_addresses,
        default_address=default_address,
        min_date_str=min_date_str,
        time_slots=time_slots
    )


@bp.route('/success/<order_number>')
def order_success(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    shop_setting = ShopSetting.get_settings()
    vietqr_url = None
    if order.payment_method == 'BANK_TRANSFER':
        # Generate VietQR quick link
        bank = shop_setting.bank_code
        acc = shop_setting.bank_account_no
        amt = int(order.total_amount)
        desc = f"FLORA {order.order_number}"
        vietqr_url = f"https://img.vietqr.io/image/{bank}-{acc}-compact2.png?amount={amt}&addInfo={desc}&accountName={shop_setting.bank_account_name}"

    return render_template(
        'shop/order_success.html',
        order=order,
        payment=order.payment,
        shop_setting=shop_setting,
        setting=shop_setting,
        vietqr_url=vietqr_url
    )


@bp.route('/tracking', methods=['GET', 'POST'])
def tracking():
    order = None
    if request.method == 'POST':
        order_number = request.form.get('order_number', '').strip().upper()
        phone = request.form.get('phone', '').strip()
        if order_number and phone:
            order = Order.query.filter(
                Order.order_number == order_number,
                (Order.sender_phone == phone) | (Order.recipient_phone == phone)
            ).first()
            if not order:
                flash('Không tìm thấy thông tin đơn hàng khớp với mã đơn và số điện thoại.', 'warning')
        else:
            flash('Vui lòng nhập cả mã đơn hàng và số điện thoại liên hệ.', 'warning')

    return render_template('shop/order_tracking.html', order=order)


@bp.route('/detail/<order_number>')
@login_required
def detail(order_number):
    order = Order.query.filter_by(order_number=order_number, user_id=current_user.id).first_or_404()
    cancel_form = OrderCancelForm()
    shop_setting = ShopSetting.get_settings()
    vietqr_url = None
    if order.payment_method == 'BANK_TRANSFER':
        bank = shop_setting.bank_code
        acc = shop_setting.bank_account_no
        amt = int(order.total_amount)
        desc = f"FLORA {order.order_number}"
        vietqr_url = f"https://img.vietqr.io/image/{bank}-{acc}-compact2.png?amount={amt}&addInfo={desc}&accountName={shop_setting.bank_account_name}"

    return render_template(
        'shop/order_detail.html',
        order=order,
        payment=order.payment,
        cancel_form=cancel_form,
        shop_setting=shop_setting,
        setting=shop_setting,
        vietqr_url=vietqr_url
    )


@bp.route('/upload-proof/<order_number>', methods=['POST'])
@login_required
def upload_proof(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    if order.user_id != current_user.id and not current_user.is_store_staff():
        flash('Bạn không có quyền gửi biên lai cho đơn hàng này.', 'danger')
        return redirect(url_for('orders.detail', order_number=order_number))

    if 'proof_image' not in request.files:
        flash('Vui lòng chọn file ảnh biên lai chuyển khoản.', 'warning')
        return redirect(url_for('orders.detail', order_number=order_number))

    file = request.files['proof_image']
    if not file or file.filename == '':
        flash('Chưa có file ảnh biên lai được chọn.', 'warning')
        return redirect(url_for('orders.detail', order_number=order_number))

    import os
    from werkzeug.utils import secure_filename
    from flask import current_app
    filename = secure_filename(f"proof_{order.order_number}_{file.filename}")
    proof_dir = os.path.join(current_app.config['MEDIA_FOLDER'], 'payments', 'proofs')
    os.makedirs(proof_dir, exist_ok=True)
    file_path = os.path.join(proof_dir, filename)
    file.save(file_path)

    payment = order.payment
    if not payment:
        payment = PaymentTransaction(
            order_id=order.id,
            payment_method='BANK_TRANSFER',
            amount=order.total_amount,
            status='WAITING_VERIFICATION'
        )
        db.session.add(payment)

    payment.proof_image = f"payments/proofs/{filename}"
    payment.status = 'WAITING_VERIFICATION'
    payment.proof_uploaded_at = datetime.utcnow()
    db.session.commit()

    flash('Đã gửi ảnh biên lai thành công! Nhân viên sẽ đối soát và xử lý đơn ngay.', 'success')
    return redirect(url_for('orders.detail', order_number=order_number))


@bp.route('/reorder/<order_number>', methods=['POST'])
@login_required
def reorder(order_number):
    order = Order.query.filter_by(order_number=order_number, user_id=current_user.id).first_or_404()
    cart = get_current_cart(current_user)
    added_count = 0

    for item in order.items.all():
        if item.product_variant_id:
            from app.models.catalog import ProductVariant
            variant = ProductVariant.query.get(item.product_variant_id)
            if variant and variant.stock > 0 and (not variant.product or variant.product.is_active):
                qty = min(item.quantity, variant.stock)
                from app.models.cart import CartItem
                cart_item = cart.items.filter_by(variant_id=variant.id).first()
                if cart_item:
                    cart_item.quantity += qty
                else:
                    cart_item = CartItem(
                        cart_id=cart.id,
                        variant_id=variant.id,
                        quantity=qty
                    )
                    db.session.add(cart_item)
                added_count += 1

    db.session.commit()
    if added_count > 0:
        flash(f'Đã thêm {added_count} mẫu hoa từ đơn #{order.order_number} vào giỏ hàng của bạn.', 'success')
        return redirect(url_for('cart.view_cart'))
    else:
        flash('Các mẫu hoa trong đơn cũ hiện tạm thời hết hàng.', 'warning')
        return redirect(url_for('orders.detail', order_number=order_number))


@bp.route('/cancel/<order_number>', methods=['POST'])
@login_required
def cancel_order(order_number):
    order = Order.query.filter_by(order_number=order_number, user_id=current_user.id).first_or_404()
    if not order.can_cancel_by_customer:
        flash('Đơn hàng đã được xử lý hoặc chuẩn bị hoa, không thể tự hủy.', 'danger')
        return redirect(url_for('orders.detail', order_number=order_number))

    form = OrderCancelForm()
    if form.validate_on_submit():
        order.status = 'CANCELLED'
        order.cancelled_at = datetime.utcnow()
        order.cancelled_by_id = current_user.id
        order.cancellation_reason = form.cancellation_reason.data.strip()

        history = OrderStatusHistory(
            order_id=order.id,
            from_status='PENDING',
            to_status='CANCELLED',
            note=f"Khách hàng hủy đơn: {order.cancellation_reason}",
            changed_by_id=current_user.id
        )
        db.session.add(history)

        # Restore inventory stock
        record_order_cancellation(order, performed_by=current_user, reason=order.cancellation_reason)

        db.session.commit()
        flash('Đơn hàng đã được hủy thành công. Số lượng tồn kho đã được hoàn lại.', 'info')

    return redirect(url_for('orders.detail', order_number=order_number))


@bp.route('/my-orders')
@login_required
def my_orders():
    orders = current_user.orders.order_by(Order.created_at.desc()).all()
    return render_template('accounts/orders.html', orders=orders)

