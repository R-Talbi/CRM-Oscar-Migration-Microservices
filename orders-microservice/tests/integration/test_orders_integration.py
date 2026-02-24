
    # Integration Tests für API-Orders


from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from orders.models import Order, OrderLine


class TestOrderAPI(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_order_erstellen(self):

        response = self.client.post('/api/orders/', {
            'number': '100001',
            'customer_id': 1,
            'basket_id': 1,
            'currency': 'EUR',
            'total_incl_tax': '119.00',
            'total_excl_tax': '100.00',
            'shipping_incl_tax': '5.95',
            'shipping_excl_tax': '5.00',
            'status': 'Pending'
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['number'], '100001')

    def test_order_status_aendern(self):

        order = Order.objects.create(
            number='100001',
            customer_id=1,
            basket_id=1,
            currency='EUR',
            total_incl_tax=Decimal('100.00'),
            total_excl_tax=Decimal('84.03'),
            status='Pending'
        )
        response = self.client.post(
            f'/api/orders/{order.id}/set_status/',
            {'status': 'Processing'},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'Processing')

    def test_line_hinzufuegen(self):
        order = Order.objects.create(
            number='100001',
            customer_id=1,
            basket_id=1,
            currency='EUR',
            total_incl_tax=Decimal('100.00'),
            total_excl_tax=Decimal('84.03'),
            status='Pending'
        )
        response = self.client.post(
            f'/api/orders/{order.id}/add_line/',
            {
                'product_id': 1,
                'title': 'Sommer-Shirt',
                'partner_sku': 'SKU001',
                'quantity': 2,
                'line_price_incl_tax': '59.50',
                'line_price_excl_tax': '50.00',
                'line_price_before_discounts_incl_tax': '59.50',
                'line_price_before_discounts_excl_tax': '50.00',
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['product_id'], 1)

    def test_note_hinzufuegen(self):
        order = Order.objects.create(
            number='100001',
            customer_id=1,
            basket_id=1,
            currency='EUR',
            total_incl_tax=Decimal('100.00'),
            total_excl_tax=Decimal('84.03'),
            status='Pending'
        )
        response = self.client.post(
            f'/api/orders/{order.id}/add_note/',
            {'message': 'Test Note', 'note_type': 'Info'},
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['message'], 'Test Note')
