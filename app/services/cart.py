import uuid
from flask import session
from app.extensions import db
from app.models.cart import Cart, CartItem, CartItemAccessory
from app.models.catalog import ProductVariant, Accessory
from app.models.promotion import Coupon

def get_current_cart(user=None):
    """Retrieves or creates active cart for current user or session."""
    if user and user.is_authenticated:
        cart = Cart.query.filter_by(user_id=user.id).order_by(Cart.updated_at.desc()).first()
        if not cart:
            cart = Cart(user_id=user.id)
            db.session.add(cart)
            db.session.commit()
        return cart
    else:
        session_key = session.get('cart_session_key')
        if not session_key:
            session_key = str(uuid.uuid4())
            session['cart_session_key'] = session_key

        cart = Cart.query.filter_by(session_key=session_key).first()
        if not cart:
            cart = Cart(session_key=session_key)
            db.session.add(cart)
            db.session.commit()
        return cart


def merge_guest_cart_to_user(session_key, user):
    """When a guest user logs in, merges their session cart into their account cart."""
    if not session_key or not user or not user.is_authenticated:
        return

    guest_cart = Cart.query.filter_by(session_key=session_key).first()
    if not guest_cart or guest_cart.items.count() == 0:
        return

    user_cart = Cart.query.filter_by(user_id=user.id).order_by(Cart.updated_at.desc()).first()
    if not user_cart:
        guest_cart.user_id = user.id
        guest_cart.session_key = None
        db.session.commit()
        return

    # Merge items
    for g_item in guest_cart.items.all():
        existing_item = user_cart.items.filter_by(variant_id=g_item.variant_id).first()
        if existing_item:
            existing_item.quantity += g_item.quantity
            db.session.delete(g_item)
        else:
            g_item.cart_id = user_cart.id

    if guest_cart.coupon_id and not user_cart.coupon_id:
        user_cart.coupon_id = guest_cart.coupon_id

    db.session.delete(guest_cart)
    db.session.commit()


def add_item_to_cart(cart, variant_id, quantity=1, card_message='', card_sender_name='', is_anonymous=False, accessory_ids=None):
    variant = db.session.get(ProductVariant, variant_id)
    if not variant:
        return False, "Sản phẩm không tồn tại"

    if variant.stock < quantity:
        return False, f"Số lượng tồn kho chỉ còn {variant.stock} sản phẩm"

    item = cart.items.filter_by(variant_id=variant.id).first()
    if item:
        new_qty = item.quantity + quantity
        if new_qty > variant.stock:
            return False, f"Không thể thêm. Tổng số lượng ({new_qty}) vượt quá tồn kho ({variant.stock})"
        item.quantity = new_qty
        if card_message:
            item.card_message = card_message
        if card_sender_name:
            item.card_sender_name = card_sender_name
        item.is_anonymous = is_anonymous
    else:
        item = CartItem(
            cart_id=cart.id,
            variant_id=variant.id,
            quantity=quantity,
            card_message=card_message,
            card_sender_name=card_sender_name,
            is_anonymous=is_anonymous
        )
        db.session.add(item)
        db.session.flush()

    # Add accessories
    if accessory_ids:
        for acc_id in accessory_ids:
            acc = Accessory.query.get(acc_id)
            if acc:
                item_acc = item.accessories.filter_by(accessory_id=acc.id).first()
                if not item_acc:
                    db.session.add(CartItemAccessory(cart_item_id=item.id, accessory_id=acc.id, quantity=1))

    db.session.commit()
    return True, "Đã thêm hoa vào giỏ hàng thành công!"
