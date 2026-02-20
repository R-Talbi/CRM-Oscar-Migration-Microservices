"""
Unit Tests - Catalogue Microservice

Strangler Pattern:
Oscar catalogue.Product → eigenständiger Microservice!
Keine Abhängigkeiten zu Oscar oder Monolith!
"""
from decimal import Decimal
from django.test import TestCase
from catalogue.models import Product


class TestProduct(TestCase):
    """
    Testet Product Model.
    Einfaches Model ohne Oscar FKs!
    """

    def setUp(self):
        self.product = Product.objects.create(
            title='Sommer-Shirt',
            description='Schönes Sommerhemd',
            price=Decimal('29.99'),
            stock=100,
            is_available=True
        )

    def test_product_erstellt(self):
        """Product kann ohne Oscar erstellt werden"""
        self.assertEqual(self.product.title, 'Sommer-Shirt')
        self.assertEqual(self.product.price, Decimal('29.99'))
        self.assertEqual(self.product.stock, 100)

    def test_product_verfügbar(self):
        self.assertTrue(self.product.is_available)

    def test_product_nicht_verfügbar(self):
        self.product.is_available = False
        self.product.save()
        self.assertFalse(self.product.is_available)

    def test_product_string(self):
        self.assertEqual(str(self.product), 'Sommer-Shirt')

    def test_date_created_automatisch(self):
        self.assertIsNotNone(self.product.date_created)

    def test_stock_update(self):
        self.product.stock = 50
        self.product.save()
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 50)

    def test_kein_oscar_fk(self):
        """
        Strangler Pattern Test:
        Product hat keine FKs zu Oscar Models!
        Vollständig unabhängig!
        """
        fields = [f.name for f in Product._meta.get_fields()]
        self.assertNotIn('productclass', fields)
        self.assertNotIn('stockrecords', fields)
        self.assertNotIn('categories', fields)
