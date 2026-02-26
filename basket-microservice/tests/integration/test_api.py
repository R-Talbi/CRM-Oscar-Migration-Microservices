"""Integration Tests für Basket-Service"""
from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from basket.models import Basket, BasketLine


class TestBasketAPI(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_basket_erstellen(self):
        # Neues Basket erstellen

        response = self.client.post('/api/basket/', {
            'customer_id': 1,
            'customer_email': 'test@example.com'
        }, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'Open')

    def test_basket_liste(self):
        Basket.objects.create(customer_id=1)
        Basket.objects.create(customer_id=2)

        response = self.client.get('/api/basket/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)

    def test_produkt_hinzufuegen_api(self):
        basket = Basket.objects.create(customer_id=1)
        response = self.client.post(
            f'/api/basket/{basket.id}/add_product/',
            {
                'product_id': 1,
                'product_title': 'Sommer-Shirt',
                'price_excl_tax': '25.00',
                'price_incl_tax': '29.75',
                'quantity': 2
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        basket.refresh_from_db()
        self.assertEqual(basket.num_items, 2)

    def test_basket_freeze_api(self):
        basket = Basket.objects.create(customer_id=1)
        response = self.client.post(f'/api/basket/{basket.id}/freeze/')
        self.assertEqual(response.status_code, 200)
        basket.refresh_from_db()
        self.assertEqual(basket.status, 'Frozen')

    def test_basket_submit_api(self):
        basket = Basket.objects.create(customer_id=1)
        response = self.client.post(f'/api/basket/{basket.id}/submit/')
        self.assertEqual(response.status_code, 200)
        basket.refresh_from_db()
        self.assertEqual(basket.status, 'Submitted')

    def test_basket_total_api(self):
        basket = Basket.objects.create(customer_id=1)
        basket.add_product(
            product_id=1,
            product_title='Shirt',
            price_excl_tax=Decimal('25.00'),
            price_incl_tax=Decimal('29.75'),
            quantity=2
        )
        response = self.client.get(f'/api/basket/{basket.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(float(response.data['total_excl_tax']), 50.0)
