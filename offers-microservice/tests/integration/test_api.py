from decimal import Decimal as D
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from offers.models import Range, Benefit, Condition, ConditionalOffer


class TestOfferApply(TestCase):
    """Wichtige Schnittstelle"""

    def setUp(self):
        self.client = APIClient()

        # Range, Condition, Benefit erstellen
        range_obj = Range.objects.create(name='Range', slug='range')
        condition = Condition.objects.create(
            range=range_obj,
            type='Value',
            value=D('50.00')
        )
        benefit = Benefit.objects.create(
            range=range_obj,
            type='Percentage',
            value=D('10.00')
        )

        # Offer erstellen
        self.offer = ConditionalOffer.objects.create(
            name='Test Offer',
            slug='test-offer',
            condition=condition,
            benefit=benefit
        )

    def test_offer_anwenden_success(self):
        response = self.client.post(
            f'/api/offers/{self.offer.id}/apply/',
            {'basket_total': '100.00', 'basket_quantity': 2},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['discount']), 10.0)

        self.offer.refresh_from_db()
        self.assertEqual(self.offer.num_applications, 1)

    def test_offer_anwenden_condition_nicht_erfuellt(self):
        """Kein Rabatt wenn Condition nicht erfüllt"""

        response = self.client.post(
            f'/api/offers/{self.offer.id}/apply/',
            {'basket_total': '30.00', 'basket_quantity': 1},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['discount']), 0.0)

    def test_offer_anwenden_suspended(self):
        """Offer darf nicht angewendet werden wenn Suspended"""
        self.offer.status = 'Suspended'
        self.offer.save()

        response = self.client.post(
            f'/api/offers/{self.offer.id}/apply/',
            {'basket_total': '100.00', 'basket_quantity': 2},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['discount']), 0.0)


class TestAvailableOffers(TestCase):
    """Verfügbare Offers abrufen"""

    def setUp(self):
        self.client = APIClient()

        range_obj = Range.objects.create(name='Range', slug='range')
        condition = Condition.objects.create(
            range=range_obj,
            type='Value',
            value=D('50.00')
        )
        benefit = Benefit.objects.create(
            range=range_obj,
            type='Percentage',
            value=D('10.00')
        )

        ConditionalOffer.objects.create(
            name='Open', slug='open',
            condition=condition, benefit=benefit, status='Open'
        )
        ConditionalOffer.objects.create(
            name='Suspended', slug='suspended',
            condition=condition, benefit=benefit, status='Suspended'
        )

    def test_nur_verfuegbare_offers(self):
        response = self.client.get('/api/offers/available/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'Open')


class TestOfferCreate(TestCase):
    """Offer erstellen"""

    def setUp(self):
        self.client = APIClient()

        range_obj = Range.objects.create(name='Range', slug='range')
        self.condition = Condition.objects.create(
            range=range_obj, type='Value', value=D('50.00')
        )
        self.benefit = Benefit.objects.create(
            range=range_obj, type='Percentage', value=D('10.00')
        )

    def test_offer_erstellen_success(self):
        response = self.client.post('/api/offers/', {
            'name': 'New Offer',
            'slug': 'new-offer',
            'condition': self.condition.id,
            'benefit': self.benefit.id,
            'offer_type': 'Site'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Offer')
        self.assertEqual(response.data['status'], 'Open')

    def test_offer_erstellen_validation_error(self):
        response = self.client.post('/api/offers/', {
            'name': '',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)