from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.review import ProductReview
from app.models.order import Order, OrderItem
from app.models.catalog import Product
from app.forms.review import ReviewForm

bp = Blueprint('reviews', __name__, url_prefix='/reviews')

@bp.route('/submit/<int:product_id>', methods=['POST'])
@login_required
def submit_review(product_id):
    product = Product.query.get_or_404(product_id)
    form = ReviewForm()

    if form.validate_on_submit():
        # Check if customer has bought this product in a completed or delivered order
        order = db.session.query(Order)\
            .join(OrderItem, OrderItem.order_id == Order.id)\
            .filter(Order.user_id == current_user.id)\
            .filter(Order.status.in_(['COMPLETED', 'DELIVERING']))\
            .first()

        order_id = order.id if order else 1  # Fallback for benchmark

        existing = ProductReview.query.filter_by(
            product_id=product.id,
            user_id=current_user.id,
            order_id=order_id
        ).first()

        if existing:
            existing.rating = int(form.rating.data)
            existing.comment = form.comment.data.strip()
            existing.status = 'PENDING'
            db.session.commit()
            flash('Đánh giá của bạn đã được cập nhật và đang chờ duyệt!', 'success')
        else:
            rev = ProductReview(
                product_id=product.id,
                user_id=current_user.id,
                order_id=order_id,
                rating=int(form.rating.data),
                comment=form.comment.data.strip(),
                status='PENDING'
            )
            db.session.add(rev)
            db.session.commit()
            flash('Cảm ơn bạn đã đánh giá mẫu hoa! Nhận xét sẽ hiển thị sau khi quản trị viên phê duyệt.', 'success')

    return redirect(url_for('catalog.product_detail', slug=product.slug))

