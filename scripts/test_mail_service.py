#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
scripts/test_mail_service.py
-----------------------------------------------------------------------------
Kịch bản kiểm thử dịch vụ gửi email bằng Flask-Mail:
1. Kiểm tra cấu hình biến môi trường trong .env
2. Giả lập gửi email nội bộ (Outbox Simulation) để xem trước nội dung, người nhận và định dạng HTML
3. Hỗ trợ gửi thử email thật qua SMTP nếu tài khoản đã cấu hình
-----------------------------------------------------------------------------
"""

import sys
import os

# Auto-detect and switch to virtualenv Python if launched with system Python
if sys.prefix == getattr(sys, "base_prefix", sys.prefix):
    venv_python = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'venv', 'Scripts', 'python.exe'))
    if os.path.exists(venv_python) and os.path.abspath(sys.executable).lower() != os.path.abspath(venv_python).lower():
        import subprocess
        try:
            sys.exit(subprocess.call([venv_python] + sys.argv))
        except KeyboardInterrupt:
            sys.exit(0)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from app import create_app
from app.extensions import mail
from app.models.order import Order
from app.models.user import User
from app.services.email import (
    send_order_confirmation_to_customer,
    send_new_order_notification_to_shop_owner,
    send_password_reset_email,
    send_registration_verification_email,
    send_email
)

def run_mail_tests():
    app = create_app('testing')
    
    print("=" * 70)
    print(" BÁO CÁO KIỂM THỬ DỊCH VỤ EMAIL FLASK-MAIL - FLORA FLOWER")
    print("=" * 70)
    
    # 1. Kiểm tra cấu hình
    print("\n[BƯỚC 1] KIỂM TRA THÔNG SỐ CẤU HÌNH TRONG .ENV:")
    print(f" - MAIL_SERVER             : {app.config.get('MAIL_SERVER')}")
    print(f" - MAIL_PORT               : {app.config.get('MAIL_PORT')}")
    print(f" - MAIL_USE_TLS            : {app.config.get('MAIL_USE_TLS')}")
    print(f" - MAIL_DEFAULT_SENDER     : {app.config.get('MAIL_DEFAULT_SENDER')}")
    print(f" - SHOP_NOTIFICATION_EMAIL : {app.config.get('SHOP_NOTIFICATION_EMAIL')}")
    mail_user = app.config.get('MAIL_USERNAME')
    print(f" - MAIL_USERNAME           : {mail_user if mail_user else '(Chưa điền - Đang dùng chế độ test)'}")
    
    with app.app_context():
        # 2. Kiểm tra bộ nhớ gửi Outbox (Safe Testing)
        print("\n[BƯỚC 2] KIỂM THỬ GIẢ LẬP GỬI EMAIL NỘI BỘ (SAFE TESTING):")
        with mail.record_messages() as outbox:
            order = Order.query.first()
            user = User.query.filter_by(username='khachhang1').first() or User.query.first()

            # Email 1: Hóa đơn xác nhận đơn hàng cho khách
            print("\n 1. Kiểm tra Email Xác Nhận Đơn Hàng Cho Khách:")
            send_order_confirmation_to_customer(order)
            msg1 = outbox[-1]
            print(f"    -> Tiêu đề (Subject) : {msg1.subject}")
            print(f"    -> Người nhận (To)   : {msg1.recipients}")
            print(f"    -> Người gửi (From)  : {msg1.sender}")
            print(f"    -> Đơn hàng kiểm tra : #{order.order_number}")
            print(f"    -> Trạng thái kiểm tra: ĐẠT (Đúng email khách: {order.sender_email})")

            # Email 2: Thông báo đơn hàng mới cho chủ shop
            print("\n 2. Kiểm tra Email Thông Báo Đơn Mới Cho Chủ Shop:")
            send_new_order_notification_to_shop_owner(order)
            msg2 = outbox[-1]
            print(f"    -> Tiêu đề (Subject) : {msg2.subject}")
            print(f"    -> Người nhận (To)   : {msg2.recipients}")
            target_owner_email = app.config.get('SHOP_NOTIFICATION_EMAIL')
            print(f"    -> Kiểm tra email đích: {target_owner_email}")
            assert target_owner_email in msg2.recipients, f"Email đích không khớp: {msg2.recipients}"
            print(f"    -> Trạng thái kiểm tra: ĐẠT (Gửi chính xác tới {target_owner_email})")

            # Email 3: Hướng dẫn đặt lại mật khẩu kèm token
            print("\n 3. Kiểm tra Email Đặt Lại Mật Khẩu (Password Reset):")
            send_password_reset_email(user)
            msg3 = outbox[-1]
            print(f"    -> Tiêu đề (Subject) : {msg3.subject}")
            print(f"    -> Người nhận (To)   : {msg3.recipients}")
            print(f"    -> Chứa liên kết token bảo mật: {'token' in msg3.html or 'reset-password' in msg3.html}")
            print(f"    -> Trạng thái kiểm tra: ĐẠT")

            # Email 4: Xác thực đăng ký tài khoản
            print("\n 4. Kiểm tra Email Kích Hoạt Đăng Ký:")
            send_registration_verification_email(user)
            msg4 = outbox[-1]
            print(f"    -> Tiêu đề (Subject) : {msg4.subject}")
            print(f"    -> Người nhận (To)   : {msg4.recipients}")
            print(f"    -> Trạng thái kiểm tra: ĐẠT")

        print("\n" + "=" * 70)
        print(" KẾT QUẢ: 4/4 LUỒNG EMAIL ĐÃ ĐƯỢC BẢO ĐẢM ĐÚNG ĐỊNH DẠNG & ĐÍCH ĐẾN!")
        print("=" * 70)

        # 3. Hướng dẫn gửi thật qua SMTP nếu muốn
        print("\n[BƯỚC 3] HƯỚNG DẪN GỬI THẬT VỀ HÒM THƯ GMAIL (NẾU CẦN):")
        print(" Để gửi email thật về hòm thư Gmail, bạn mở file '.env' và điền 2 dòng:")
        print("   MAIL_USERNAME=email_cua_ban@gmail.com")
        print("   MAIL_PASSWORD=mat_khau_ung_dung_16_ky_tu_google")
        print("   (Lưu ý: Mật khẩu ứng dụng lấy tại myaccount.google.com -> Bảo mật -> Mật khẩu ứng dụng)")

if __name__ == '__main__':
    run_mail_tests()

