import os
import logging
from datetime import datetime
from threading import Thread
from flask import current_app, render_template, url_for
from flask_mail import Message
from app.extensions import mail

logger = logging.getLogger(__name__)

def log_email_to_file(subject, recipients, html_body):
    """Lưu toàn bộ nội dung email phát đi vào logs/emails.log để phục vụ kiểm tra và thuyết trình."""
    os.makedirs('logs', exist_ok=True)
    with open('logs/emails.log', 'a', encoding='utf-8') as f:
        f.write(f"\n{'='*75}\n")
        f.write(f"THỜI GIAN: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"NGƯỜI NHẬN: {recipients}\n")
        f.write(f"TIÊU ĐỀ: {subject}\n")
        f.write(f"{'-'*75}\n")
        f.write(html_body)
        f.write(f"\n{'='*75}\n")

def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
            logger.info(f"Email sent successfully via SMTP to: {msg.recipients}")
        except Exception as e:
            logger.error(f"Failed to send email to {msg.recipients} via SMTP: {e}")

def send_email(subject, recipients, html_body, text_body=None, sync=False):
    app = current_app._get_current_object()
    sender = app.config.get('MAIL_DEFAULT_SENDER', 'Flora Flower <noreply@floraflower.vn>')
    recipients_list = recipients if isinstance(recipients, list) else [recipients]

    msg = Message(
        subject=f"[Flora Flower] {subject}",
        sender=sender,
        recipients=recipients_list
    )
    msg.html = html_body
    msg.body = text_body or "Vui lòng xem email này trong ứng dụng hỗ trợ HTML."

    # 1. Luôn ghi log chi tiết vào file logs/emails.log phục vụ kiểm tra/bảo vệ đồ án
    try:
        log_email_to_file(msg.subject, msg.recipients, msg.html)
    except Exception as e:
        logger.warning(f"Could not write to email log: {e}")

    # 2. Chế độ kiểm thử (TESTING) - Flask-Mail lưu trong bộ nhớ outbox
    if app.config.get('TESTING'):
        try:
            mail.send(msg)
            return True, "Email recorded in test outbox"
        except Exception as e:
            logger.warning(f"Test mail send failed: {e}")
            return False, str(e)

    # 3. Kiểm tra tài khoản SMTP trong file .env
    mail_username = app.config.get('MAIL_USERNAME')
    mail_password = app.config.get('MAIL_PASSWORD')

    if not mail_username or not mail_password:
        logger.info(f"[EMAIL DEV LOG] Đã ghi nhận email gửi tới {recipients_list}: '{msg.subject}' vào logs/emails.log.")
        return True, "Email recorded in local log (SMTP credentials not configured in .env)"

    # 4. Khi đã có cấu hình SMTP thật, tiến hành gửi qua Internet
    if sync:
        try:
            mail.send(msg)
            logger.info(f"[SMTP LIVE] Đã phát email thật tới: {msg.recipients}")
            return True, "Email sent via SMTP"
        except Exception as e:
            logger.warning(f"SMTP delivery failed: {e}")
            return False, str(e)
    else:
        # Gửi nền đa luồng (Async Thread) không làm đơ giao diện đặt hàng
        Thread(target=send_async_email, args=(app, msg)).start()
        return True, "Email queued for SMTP"


def send_registration_verification_email(user):
    token = user.get_token(salt='email-confirm', expires_sec=86400)
    base_url = current_app.config.get('PUBLIC_BASE_URL', 'http://127.0.0.1:5000')
    confirm_url = f"{base_url}/accounts/verify-email/{token}"

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e5e7eb; border-radius: 8px;">
        <h2 style="color: #234D3C;">Chào mừng {user.full_name} đến với Flora Flower!</h2>
        <p>Cảm ơn bạn đã đăng ký tài khoản tại Flora Flower Boutique. Vui lòng xác thực địa chỉ email để kích hoạt đầy đủ tính năng ưu đãi thành viên.</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{confirm_url}" style="background-color: #234D3C; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                Xác Thực Tài Khoản Ngay
            </a>
        </div>
        <p style="font-size: 13px; color: #6b7280;">Liên kết này có hiệu lực trong vòng 24 giờ. Nếu bạn không tạo tài khoản này, vui lòng bỏ qua email.</p>
    </div>
    """
    return send_email("Xác nhận đăng ký tài khoản", user.email, html)


def send_password_reset_email(user):
    token = user.get_token(salt='password-reset', expires_sec=3600)
    base_url = current_app.config.get('PUBLIC_BASE_URL', 'http://127.0.0.1:5000')
    reset_url = f"{base_url}/accounts/reset-password/{token}"

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e5e7eb; border-radius: 8px;">
        <h2 style="color: #234D3C;">Yêu cầu đặt lại mật khẩu</h2>
        <p>Xin chào {user.full_name}, chúng tôi nhận được yêu cầu đổi mật khẩu cho tài khoản {user.username}.</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_url}" style="background-color: #C07080; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                Đặt Lại Mật Khẩu Mới
            </a>
        </div>
        <p style="font-size: 13px; color: #6b7280;">Liên kết này có hiệu lực trong 60 phút. Tuyệt đối không chia sẻ liên kết này cho bất kỳ ai.</p>
    </div>
    """
    return send_email("Hướng dẫn đặt lại mật khẩu", user.email, html)


def send_order_confirmation_to_customer(order):
    """Sends detailed order receipt to customer's personal email."""
    items_html = ""
    for item in order.items:
        items_html += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{item.product_name} ({item.variant_name}) x {item.quantity}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: right;">{int(item.subtotal):,} đ</td>
        </tr>
        """

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 650px; margin: 0 auto; padding: 20px; border: 1px solid #e5e7eb; border-radius: 8px;">
        <h2 style="color: #234D3C; margin-bottom: 5px;">Cảm ơn bạn đã đặt hoa tại Flora Flower!</h2>
        <p style="color: #4b5563;">Đơn hàng <strong>#{order.order_number}</strong> của bạn đã được tiếp nhận thành công.</p>
        
        <div style="background-color: #f9fafb; padding: 15px; border-radius: 6px; margin: 20px 0;">
            <h4 style="margin-top: 0; color: #234D3C;">Thông Tin Giao Hoa</h4>
            <p style="margin: 5px 0;"><strong>Người nhận:</strong> {order.recipient_name} ({order.recipient_phone})</p>
            <p style="margin: 5px 0;"><strong>Địa chỉ:</strong> {order.full_delivery_address}</p>
            <p style="margin: 5px 0;"><strong>Lịch giao:</strong> {order.delivery_date.strftime('%d/%m/%Y')} ({order.delivery_time_slot})</p>
            {f'<p style="margin: 5px 0;"><strong>Lời chúc thiệp:</strong> "{order.card_message}"</p>' if order.card_message else ''}
        </div>

        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
            <thead>
                <tr style="background-color: #f3f4f6;">
                    <th style="padding: 8px; text-align: left;">Sản phẩm</th>
                    <th style="padding: 8px; text-align: right;">Thành tiền</th>
                </tr>
            </thead>
            <tbody>
                {items_html}
            </tbody>
            <tfoot>
                <tr>
                    <td style="padding: 8px; font-weight: bold;">Tổng tiền thanh toán:</td>
                    <td style="padding: 8px; text-align: right; font-weight: bold; color: #234D3C; font-size: 16px;">{int(order.total_amount):,} đ</td>
                </tr>
                <tr>
                    <td style="padding: 8px;">Hình thức thanh toán:</td>
                    <td style="padding: 8px; text-align: right;">{order.payment_method}</td>
                </tr>
            </tfoot>
        </table>
        
        <p style="font-size: 13px; color: #6b7280;">Mọi thắc mắc vui lòng liên hệ Hotline: 1900 6868 hoặc phản hồi email này.</p>
    </div>
    """
    return send_email(f"Xác nhận đơn hàng #{order.order_number}", order.sender_email, html)


def send_new_order_notification_to_shop_owner(order):
    """
    Sends new order alert to the shop administrator email
    Configured strictly through SHOP_NOTIFICATION_EMAIL (phuongtruong121204@gmail.com).
    """
    shop_email = current_app.config.get('SHOP_NOTIFICATION_EMAIL', 'phuongtruong121204@gmail.com')
    if not shop_email:
        logger.warning("SHOP_NOTIFICATION_EMAIL is not set. Skipping owner alert.")
        return False, "No owner email configured"

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 650px; margin: 0 auto; padding: 20px; border: 2px solid #234D3C; border-radius: 8px;">
        <h2 style="color: #234D3C; margin-top: 0;">🔔 THÔNG BÁO ĐƠN HÀNG MỚI #{order.order_number}</h2>
        <p>Hệ thống Flora Flower vừa ghi nhận một đơn đặt hoa mới từ website.</p>
        
        <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
            <tr>
                <td style="padding: 6px; font-weight: bold; width: 140px;">Khách đặt:</td>
                <td style="padding: 6px;">{order.sender_name} - {order.sender_phone} ({order.sender_email})</td>
            </tr>
            <tr>
                <td style="padding: 6px; font-weight: bold;">Người nhận:</td>
                <td style="padding: 6px;">{order.recipient_name} - {order.recipient_phone}</td>
            </tr>
            <tr>
                <td style="padding: 6px; font-weight: bold;">Địa chỉ:</td>
                <td style="padding: 6px;">{order.full_delivery_address}</td>
            </tr>
            <tr>
                <td style="padding: 6px; font-weight: bold;">Lịch giao:</td>
                <td style="padding: 6px;"><strong style="color: #d97706;">{order.delivery_date.strftime('%d/%m/%Y')} ({order.delivery_time_slot})</strong></td>
            </tr>
            <tr>
                <td style="padding: 6px; font-weight: bold;">Tổng tiền:</td>
                <td style="padding: 6px;"><strong style="color: #059669; font-size: 16px;">{int(order.total_amount):,} đ</strong> ({order.payment_method})</td>
            </tr>
            <tr>
                <td style="padding: 6px; font-weight: bold;">Ghi chú cắm hoa:</td>
                <td style="padding: 6px;">{order.card_message or 'Không có'}</td>
            </tr>
        </table>
        
        <div style="margin-top: 20px; text-align: center;">
            <a href="{current_app.config.get('PUBLIC_BASE_URL', 'http://127.0.0.1:5000')}/dashboard/orders/{order.id}"
               style="background-color: #234D3C; color: #fff; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                Mở Đơn Hàng Trong Quản Trị
            </a>
        </div>
    </div>
    """
    return send_email(f"[ĐƠN MỚI] #{order.order_number} - {int(order.total_amount):,} đ", shop_email, html)

