import unittest
from app import create_app
from app.extensions import db
from app.models import User, UserProfile

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_admin_and_customer_exist(self):
        admin = User.query.filter_by(username='admin').first()
        customer = User.query.filter_by(username='khachhang1').first()
        self.assertIsNotNone(admin)
        self.assertIsNotNone(customer)
        self.assertTrue(admin.is_admin())
        self.assertFalse(customer.is_admin())

    def test_django_pbkdf2_hash_verification(self):
        admin = User.query.filter_by(username='admin').first()
        customer = User.query.filter_by(username='khachhang1').first()
        self.assertTrue(admin.check_password('admin123456'))
        self.assertTrue(customer.check_password('customer123'))
        self.assertFalse(admin.check_password('wrong_password'))

    def test_role_based_access_control(self):
        # 1. Unauthenticated user accessing dashboard -> redirected to login
        res = self.client.get('/dashboard/')
        self.assertEqual(res.status_code, 302)
        self.assertIn('/accounts/login', res.headers.get('Location', ''))

        # 2. Customer accessing dashboard -> 403 Forbidden
        self.client.post('/accounts/login', data={
            'username_or_email': 'khachhang1',
            'password': 'customer123'
        })
        res = self.client.get('/dashboard/')
        self.assertEqual(res.status_code, 403)

        # 3. Admin accessing dashboard -> 200 OK
        self.client.get('/accounts/logout')
        self.client.post('/accounts/login', data={
            'username_or_email': 'admin',
            'password': 'admin123456'
        })
        res = self.client.get('/dashboard/')
        self.assertEqual(res.status_code, 200)

    def test_token_generation_and_expiration(self):
        admin = User.query.filter_by(username='admin').first()
        token = admin.get_token(salt='email-confirm', expires_sec=3600)
        self.assertIsNotNone(token)
        verified_user = User.verify_token(token, salt='email-confirm', expires_sec=3600)
        self.assertEqual(verified_user.id, admin.id)

        # Wrong salt or expired token returns None
        self.assertIsNone(User.verify_token(token, salt='wrong-salt'))

if __name__ == '__main__':
    unittest.main()
