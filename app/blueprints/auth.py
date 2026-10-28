from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import User, UserProfile, Address, Wishlist
from app.forms.auth import LoginForm, RegisterForm, RequestResetForm, ResetPasswordForm, ProfileForm, AddressForm
from app.services.email import send_registration_verification_email, send_password_reset_email
from app.services.cart import merge_guest_cart_to_user

bp = Blueprint('auth', __name__, url_prefix='/accounts')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_store_staff():
            return redirect(url_for('dashboard.overview'))
        return redirect(url_for('main.index'))

    form = LoginForm()
    if request.method == 'POST':
        ident = (request.form.get('username_or_email') or request.form.get('username') or (form.username_or_email.data or form.username.data or '')).strip()
        password = request.form.get('password') or form.password.data or ''

        if not ident or not password:
            flash('Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.', 'danger')
            return render_template('accounts/login.html', form=form)

        user = User.query.filter((User.username == ident) | (User.email == ident.lower())).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash('Tài khoản của bạn hiện đang bị khóa. Vui lòng liên hệ quản trị viên.', 'danger')
                return render_template('accounts/login.html', form=form)

            remember = bool(request.form.get('remember_me') or form.remember_me.data)
            login_user(user, remember=remember)

            # Merge session cart into account cart
            session_key = session.get('cart_session_key')
            if session_key:
                merge_guest_cart_to_user(session_key, user)

            flash(f'Chào mừng bạn trở lại, {user.full_name}!', 'success')
            next_page = request.args.get('next') or request.form.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            if user.is_store_staff():
                return redirect(url_for('dashboard.overview'))
            return redirect(url_for('main.index'))
        else:
            flash('Tên đăng nhập, email hoặc mật khẩu không chính xác.', 'danger')

    return render_template('accounts/login.html', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip().lower(),
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            is_active=True
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()

        profile = UserProfile(
            user_id=user.id,
            phone=form.phone.data.strip(),
            role='CUSTOMER'
        )
        db.session.add(profile)
        db.session.commit()

        # Send verification email via Flask-Mail
        try:
            send_registration_verification_email(user)
        except Exception:
            pass

        login_user(user)

        # Merge cart
        session_key = session.get('cart_session_key')
        if session_key:
            merge_guest_cart_to_user(session_key, user)

        flash('Đăng ký tài khoản thành công! Chúng tôi đã gửi email xác thực tài khoản đến bạn.', 'success')
        return redirect(url_for('main.index'))

    return render_template('accounts/register.html', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    flash('Bạn đã đăng xuất tài khoản an toàn.', 'info')
    return redirect(url_for('main.index'))


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    profile = current_user.profile
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        gender = request.form.get('gender', '')
        dob_str = request.form.get('date_of_birth', '').strip()

        if not full_name or not email:
            flash('Họ tên và email không được để trống.', 'danger')
            return redirect(url_for('auth.profile'))

        # Check email uniqueness if changed
        if email.lower() != current_user.email.lower():
            existing = User.query.filter(User.email == email.lower(), User.id != current_user.id).first()
            if existing:
                flash('Email này đã được sử dụng bởi một tài khoản khác.', 'danger')
                return redirect(url_for('auth.profile'))

        current_user.first_name = full_name
        current_user.email = email.lower()
        profile.phone = phone
        if gender in ['M', 'F', 'O']:
            profile.gender = gender

        if dob_str:
            try:
                profile.date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
            except Exception:
                pass

        db.session.commit()
        flash('Thông tin tài khoản đã được cập nhật thành công.', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('accounts/profile.html', user=current_user, profile=profile)


@bp.route('/addresses', methods=['GET', 'POST'])
@login_required
def addresses():
    form = AddressForm()
    if form.validate_on_submit():
        if form.is_default.data:
            Address.query.filter_by(user_id=current_user.id).update({'is_default': False})

        addr = Address(
            user_id=current_user.id,
            full_name=form.full_name.data.strip(),
            phone=form.phone.data.strip(),
            street_address=form.street_address.data.strip(),
            ward=form.ward.data.strip() if form.ward.data else '',
            district=form.district.data.strip(),
            city=form.city.data.strip(),
            is_default=form.is_default.data
        )
        db.session.add(addr)
        db.session.commit()
        flash('Đã thêm địa chỉ giao hàng mới.', 'success')
        return redirect(url_for('auth.addresses'))

    user_addresses = current_user.addresses.order_by(Address.is_default.desc(), Address.created_at.desc()).all()
    return render_template('accounts/addresses.html', addresses=user_addresses, form=form)


@bp.route('/addresses/<int:id>/delete', methods=['POST'])
@login_required
def delete_address(id):
    addr = Address.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(addr)
    db.session.commit()
    flash('Đã xóa địa chỉ thành công.', 'info')
    return redirect(url_for('auth.addresses'))


@bp.route('/wishlist')
@login_required
def wishlist():
    items = current_user.wishlist_items.order_by(Wishlist.created_at.desc()).all()
    return render_template('shop/wishlist.html', items=items)


@bp.route('/wishlist/toggle/<int:product_id>', methods=['POST'])
@login_required
def toggle_wishlist(product_id):
    item = Wishlist.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'status': 'removed', 'message': 'Đã bỏ yêu thích'})
    else:
        db.session.add(Wishlist(user_id=current_user.id, product_id=product_id))
        db.session.commit()
        return jsonify({'status': 'added', 'message': 'Đã thêm vào yêu thích'})


@bp.route('/verify-email/<token>')
def verify_email(token):
    user = User.verify_token(token, salt='email-confirm', expires_sec=86400)
    if not user:
        flash('Liên kết xác thực không hợp lệ hoặc đã hết hạn.', 'danger')
        return redirect(url_for('auth.login'))

    flash('Xác thực địa chỉ email thành công! Bạn có thể bắt đầu mua sắm.', 'success')
    return redirect(url_for('main.index'))


@bp.route('/reset-password', methods=['GET', 'POST'])
def request_reset():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user:
            send_password_reset_email(user)
        flash('Hướng dẫn đặt lại mật khẩu đã được gửi đến email của bạn nếu địa chỉ tồn tại trong hệ thống.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('accounts/password_change.html', form=form, mode='request')


@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    user = User.verify_token(token, salt='password-reset', expires_sec=3600)
    if not user:
        flash('Liên kết đổi mật khẩu không hợp lệ hoặc đã quá thời hạn 60 phút.', 'danger')
        return redirect(url_for('auth.request_reset'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Mật khẩu của bạn đã được cập nhật thành công! Vui lòng đăng nhập với mật khẩu mới.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('accounts/password_change.html', form=form, mode='reset')

