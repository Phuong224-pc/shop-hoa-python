import unittest
from app import create_app
from app.extensions import db
from app.models import Product, ProductVariant, Category, Order, OrderItem, User

class CatalogCRUDTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

        # Log in admin for dashboard routes
        with self.client.session_transaction() as sess:
            admin = User.query.filter_by(username='admin').first()
            sess['_user_id'] = str(admin.id)
            sess['_fresh'] = True

    def tearDown(self):
        self.ctx.pop()

    def test_search_and_pagination(self):
        # 1. Search by keyword
        res = self.client.get('/products?q=Hồng')
        self.assertEqual(res.status_code, 200)

        # 2. Search by SKU
        first_p = Product.query.first()
        res_sku = self.client.get(f'/products?q={first_p.sku}')
        self.assertEqual(res_sku.status_code, 200)
        self.assertIn(first_p.name.encode('utf-8'), res_sku.data)

        # 3. Filter by Category
        cat = Category.query.first()
        res_cat = self.client.get(f'/products?category={cat.slug}')
        self.assertEqual(res_cat.status_code, 200)

    def test_product_create_and_edit(self):
        cat = Category.query.first()
        test_sku = "UNITTEST-FLOWER-01"

        # Cleanup if exists
        p = Product.query.filter_by(sku=test_sku).first()
        if p:
            db.session.delete(p)
            db.session.commit()

        # Create
        res = self.client.post('/dashboard/products/create', data={
            'name': 'Hoa Unit Test Mới',
            'sku': test_sku,
            'primary_category_id': cat.id,
            'presentation_style': 'BOUQUET',
            'color_tone': 'RED',
            'short_description': 'Mô tả ngắn unit test.',
            'description': 'Mô tả chi tiết unit test.',
            'default_variant_name': 'Tiêu chuẩn',
            'default_price': '300000',
            'default_stock': '25',
            'status': 'PUBLISHED'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        created = Product.query.filter_by(sku=test_sku).first()
        self.assertIsNotNone(created)
        self.assertEqual(created.name, 'Hoa Unit Test Mới')
        self.assertEqual(created.default_variant.price, 300000)

        # Edit
        res_edit = self.client.post(f'/dashboard/products/{created.id}/edit', data={
            'name': 'Hoa Unit Test (Đã cập nhật)',
            'sku': test_sku,
            'primary_category_id': cat.id,
            'presentation_style': 'BOX',
            'color_tone': 'PINK',
            'short_description': 'Mô tả ngắn cập nhật.',
            'description': 'Mô tả chi tiết cập nhật.',
            'default_variant_name': 'Hộp hoa',
            'default_price': '350000',
            'default_stock': '30',
            'status': 'PUBLISHED'
        }, follow_redirects=True)
        self.assertEqual(res_edit.status_code, 200)

        db.session.refresh(created)
        self.assertEqual(created.name, 'Hoa Unit Test (Đã cập nhật)')
        self.assertEqual(created.default_variant.price, 350000)

        # Cleanup
        db.session.delete(created)
        db.session.commit()

    def test_safe_deletion_and_soft_delete(self):
        cat = Category.query.first()
        test_sku = "SOFTDEL-TEST-01"

        prod = Product(
            name='Hoa Test Soft Delete',
            slug='hoa-test-soft-delete',
            sku=test_sku,
            primary_category_id=cat.id,
            short_description='Mô tả',
            description='Chi tiết',
            status='PUBLISHED'
        )
        db.session.add(prod)
        db.session.flush()

        variant = ProductVariant(
            product_id=prod.id,
            name='Tiêu chuẩn',
            sku=f"{test_sku}-STD",
            price=200000,
            stock=10,
            is_default=True
        )
        db.session.add(variant)
        db.session.flush()

        # Attach an order item
        order = Order.query.first()
        item = OrderItem(
            order_id=order.id,
            product_variant_id=variant.id,
            product_name=prod.name,
            variant_name=variant.name,
            sku=variant.sku,
            unit_price=200000,
            quantity=1,
            subtotal=200000
        )
        db.session.add(item)
        db.session.commit()

        # Attempt deletion
        self.assertFalse(prod.can_be_hard_deleted())
        res = self.client.post(f'/dashboard/products/{prod.id}/delete', follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        db.session.refresh(prod)
        self.assertEqual(prod.status, 'ARCHIVED')
        self.assertTrue(prod.is_archived)

        # Cleanup
        db.session.delete(item)
        db.session.delete(prod)
        db.session.commit()

if __name__ == '__main__':
    unittest.main()

