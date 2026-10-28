import unittest
from app import create_app
from app.extensions import mail
from app.models import Order
from app.services.email import (
    send_order_confirmation_to_customer,
    send_new_order_notification_to_shop_owner
)

class MailTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_mail_sending_to_customer_and_owner(self):
        with mail.record_messages() as outbox:
            order = Order.query.first()

            # 1. Customer email
            send_order_confirmation_to_customer(order)
            self.assertEqual(len(outbox), 1)
            self.assertIn(order.sender_email, outbox[0].recipients)

            # 2. Shop owner alert strictly to SHOP_NOTIFICATION_EMAIL
            send_new_order_notification_to_shop_owner(order)
            self.assertEqual(len(outbox), 2)
            self.assertIn('phuongtruong121204@gmail.com', outbox[1].recipients)

if __name__ == '__main__':
    unittest.main()

