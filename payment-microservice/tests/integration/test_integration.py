"""
Integration Tests für Payment API
Prüfung Source und Bankcard Endpoint.
"""

from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from payment.models import SourceType, Source


class TestSourceAPI(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.source_type = SourceType.objects.create(
            name='PayPal', code='paypal'
        )

    def test_source_erstellen(self):
        response = self.client.post('/api/payment/sources/', {
            'order_id': 1,
            'order_number': '100001',
            'source_type': self.source_type.id,
            'currency': 'EUR'
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['order_id'], 1)

    def test_allocate_api(self):
        source = Source.objects.create(
            order_id=1, order_number='100001',
            source_type=self.source_type, currency='EUR'
        )
        response = self.client.post(
            f'/api/payment/sources/{source.id}/allocate/',
            {'amount': '100.00', 'reference': 'REF001'},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['amount_allocated'], '100.00')

    def test_debit_api(self):
        source = Source.objects.create(
            order_id=1, order_number='100001',
            source_type=self.source_type, currency='EUR'
        )
        source.allocate(Decimal('100.00'))
        response = self.client.post(
            f'/api/payment/sources/{source.id}/debit/',
            {'amount': '100.00'},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['amount_debited'], '100.00')

    def test_refund_api(self):
        source = Source.objects.create(
            order_id=1, order_number='100001',
            source_type=self.source_type, currency='EUR'
        )
        source.allocate(Decimal('100.00'))
        source.debit(Decimal('100.00'))
        response = self.client.post(
            f'/api/payment/sources/{source.id}/refund/',
            {'amount': '50.00'},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['amount_refunded'], '50.00')


class TestBankcardAPI(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_bankcard_erstellen(self):
        response = self.client.post('/api/payment/bankcards/', {
            'customer_id': 1,
            'card_type': 'Visa',
            'number': '1234567890123456',
            'expiry_date': '2028-12-31'
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data['number'].startswith('X'))
