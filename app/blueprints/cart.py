from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from app.extensions import db
from app.models.cart import CartItem
from app.models.promotion import Coupon
from app.models.core import ShopSetting
from app.services.cart import get_current_cart, add_item_to_cart

bp = Blueprint('cart', __name__, url_prefix='/cart')

@bp.route('/')
def view_cart():
    cart = get_current_cart(current_user)
    shop_setting = ShopSetting.get_settings()

    threshold = shop_setting.free_shipping_threshold
    needed = max(0, threshold - cart.flowers_subtotal)
    progress = 100 if needed <= 0 else min(100, int((cart.flowers_subtotal / threshold) * 100))

    return render_template(
        'shop/cart.html',
        cart=cart,
        shop_setting=shop_setting,
        amount_needed_for_free_shipping=needed,
        free_shipping_progress=progress
    )


@bp.route('/add', methods=['POST'])
def add_cart_item():
    cart = get_current_cart(current_user)
    variant_id = request.form.get('variant_id', type=int)
    quantity = request.form.get('quantity', 1, type=int)
    card_message = request.form.get('card_message', '').strip()
    card_sender_name = request.form.get('card_sender_name', '').strip()
    is_anonymous = bool(request.form.get('is_anonymous'))
    accessory_ids = request.form.getlist('accessories', type=int)

    if not variant_id:
        flash('Vui lòng chọn phiên bản hoa hợp lệ.', 'danger')
        return redirect(request.referrer or url_for('catalog.product_list'))

    success, msg = add_item_to_cart(
        cart=cart,
        variant_id=variant_id,
        quantity=max(1, quantity),
        card_message=card_message,
        card_sender_name=card_sender_name,
        is_anonymous=is_anonymous,
        accessory_ids=accessory_ids
    )

    if success:
        flash(msg, 'success')
        return redirect(url_for('cart.view_cart'))
    else:
        flash(msg, 'danger')
        return redirect(request.referrer or url_for('catalog.product_list'))


@bp.route('/update/<int:item_id>', methods=['POST'])
def update_cart_item(item_id):
    cart = get_current_cart(current_user)
    item = cart.items.filter_by(id=item_id).first_or_404()
    quantity = request.form.get('quantity', type=int)

    if quantity is None or quantity <= 0:
        db.session.delete(item)
        flash('Đã xóa món hoa khỏi giỏ hàng.', 'info')
    else:
        if quantity > item.variant.stock:
            flash(f'Số lượng yêu cầu ({quantity}) vượt quá tồn kho ({item.variant.stock}).', 'warning')
            item.quantity = item.variant.stock
        else:
            item.quantity = quantity
            flash('Cập nhật số lượng thành công.', 'success')

    db.session.commit()
    return redirect(url_for('cart.view_cart'))


@bp.route('/remove/<int:item_id>', methods=['POST'])
def remove_cart_item(item_id):
    cart = get_current_cart(current_user)
    item = cart.items.filter_by(id=item_id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    flash('Đã xóa sản phẩm khỏi giỏ hàng.', 'info')
    return redirect(url_for('cart.view_cart'))


@bp.route('/apply-coupon', methods=['POST'])
def apply_coupon():
    cart = get_current_cart(current_user)
    code = request.form.get('coupon_code', '').strip().upper()

    if not code:
        flash('Vui lòng nhập mã ưu đãi.', 'warning')
        return redirect(url_for('cart.view_cart'))

    coupon = Coupon.query.filter_by(code=code).first()
    if not coupon or not coupon.is_valid():
        flash('Mã ưu đãi không tồn tại hoặc đã hết hiệu lực sử dụng.', 'danger')
        return redirect(url_for('cart.view_cart'))

    if cart.flowers_subtotal < coupon.min_order_amount:
        flash(f'Mã {code} chỉ áp dụng cho đơn hoa từ {int(coupon.min_order_amount):,} đ trở lên.', 'warning')
        return redirect(url_for('cart.view_cart'))

    cart.coupon_id = coupon.id
    db.session.commit()
    flash(f'Đã áp dụng mã ưu đãi {code} thành công!', 'success')
    return redirect(url_for('cart.view_cart'))


@bp.route('/remove-coupon', methods=['POST'])
def remove_coupon():
    cart = get_current_cart(current_user)
    cart.coupon_id = None
    db.session.commit()
    flash('Đã gỡ bỏ mã ưu đãi.', 'info')
    return redirect(url_for('cart.view_cart'))

