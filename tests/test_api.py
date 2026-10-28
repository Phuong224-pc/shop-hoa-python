import unittest
import json
from app import create_app
from app.models import Product

class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_get_products_list(self):
        res = self.client.get('/api/v1/products')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('products', data['data'])
        self.assertIn('pagination', data['data'])

    def test_get_product_detail(self):
        p = Product.query.first()
        res = self.client.get(f'/api/v1/products/{p.id}')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['id'], p.id)
        self.assertEqual(data['data']['sku'], p.sku)

    def test_api_404_not_found(self):
        res = self.client.get('/api/v1/products/999999')
        self.assertEqual(res.status_code, 404)
        data = res.get_json()
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['code'], 404)

    def test_api_invalid_query_params(self):
        res = self.client.get('/api/v1/products?page=-1')
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertEqual(data['status'], 'error')

if __name__ == '__main__':
    unittest.main()

