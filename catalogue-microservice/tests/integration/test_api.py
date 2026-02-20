"""
Integration Tests - Catalogue API
"""
from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from catalogue.models import Product


class TestProductAPI(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_product_erstellen(self):
        response = self.client.post('/api/catalogue/', {
            'title': 'Test Produkt',
            'description': 'Test Beschreibung',
            'price': '19.99',
            'stock': 50,
            'is_available': True
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['title'], 'Test Produkt')

    def test_product_liste(self):
        Product.objects.create(
            title='Produkt 1', price=Decimal('10.00'), stock=10
        )
        Product.objects.create(
            title='Produkt 2', price=Decimal('20.00'), stock=20
        )
        response = self.client.get('/api/catalogue/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)

    def test_product_detail(self):
        product = Product.objects.create(
            title='Sommer-Shirt',
            price=Decimal('29.99'),
            stock=100
        )
        response = self.client.get(f'/api/catalogue/{product.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Sommer-Shirt')

    def test_product_update(self):
        product = Product.objects.create(
            title='Alt', price=Decimal('10.00'), stock=5
        )
        response = self.client.patch(
            f'/api/catalogue/{product.id}/',
            {'price': '15.00'},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['price'], '15.00')

    def test_product_löschen(self):
        product = Product.objects.create(
            title='Zu löschen', price=Decimal('5.00'), stock=1
        )
        response = self.client.delete(f'/api/catalogue/{product.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Product.objects.count(), 0)

    def test_health_check(self):
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)
        import json; self.assertEqual(json.loads(response.content)['status'], 'healthy')
