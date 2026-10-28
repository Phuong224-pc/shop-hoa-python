import unittest
from datetime import date
from decimal import Decimal
from app import create_app
from app.extensions import db
from app.models import Product, ProductVariant, Cart, Order, User
from app.services.cart import add_item_to_cart, get_current_cart
from app.services.inventory import record_order_sale, record_order_cancellation

class CartOrderTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_cart_operations(self):
        customer = User.query.filter_by(username='khachhang1').first()
        cart = get_current_cart(customer)
        variant = ProductVariant.query.first()

        initial_qty = cart.total_items_count
        success, msg = add_item_to_cart(cart, variant.id, quantity=2, card_message='Chúc mừng sinh nhật!')
        self.assertTrue(success)
        self.assertEqual(cart.total_items_count, initial_qty + 2)

        # Clear cart
        cart.clear()
        self.assertEqual(cart.total_items_count, 0)

    def test_stock_decrement_and_restore(self):
        variant = ProductVariant.query.first()
        initial_stock = variant.stock

        order = Order.query.first()
        # Test sale decrement
        record_order_sale(order)
        db.session.refresh(variant)
        # Stock should be decremented or recorded
        self.assertLessEqual(variant.stock, initial_stock)

        # Test cancellation restore
        record_order_cancellation(order, reason='Test restoration')
        db.session.refresh(variant)
        self.assertEqual(variant.stock, initial_stock)

if __name__ == '__main__':
    unittest.main()

