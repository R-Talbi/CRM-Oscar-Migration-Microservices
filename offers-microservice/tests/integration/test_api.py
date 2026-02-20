"""
INTEGRATION TESTS - Nur die KRITISCHSTEN Schnittstellen
Minimum Viable Tests für Production
"""
from decimal import Decimal as D
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from offers.models import Range, Benefit, Condition, ConditionalOffer


# ============================================================================
# KRITISCHSTE SCHNITTSTELLE: Offer Apply
# ============================================================================

class TestOfferApply(TestCase):
    """POST /api/offers/{id}/apply/ - WICHTIGSTE Schnittstelle!"""

    def setUp(self):
        self.client = APIClient()

        # Setup: 10% Rabatt ab 50€
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
        self.offer = ConditionalOffer.objects.create(
            name='Test Offer',
            slug='test-offer',
            condition=condition,
            benefit=benefit
        )

    def test_offer_anwenden_success(self):
        """Erfolgreiche Offer-Anwendung + Tracking"""
        response = self.client.post(
            f'/api/offers/{self.offer.id}/apply/',
            {'basket_total': '100.00', 'basket_quantity': 2},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['discount']), 10.0)

        # Tracking prüfen
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
        """Suspended Offer gibt keinen Rabatt"""
        self.offer.status = 'Suspended'
        self.offer.save()

        response = self.client.post(
            f'/api/offers/{self.offer.id}/apply/',
            {'basket_total': '100.00', 'basket_quantity': 2},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['discount']), 0.0)


# ============================================================================
# WICHTIGE SCHNITTSTELLE: Available Offers
# ============================================================================

class TestAvailableOffers(TestCase):
    """GET /api/offers/available/ - Verfügbare Offers abrufen"""

    def setUp(self):
        self.client = APIClient()

        range_obj = Range.objects.create(name='Range', slug='range')
        condition = Condition.objects.create(
            range=range_obj, type='Value', value=D('50.00')
        )
        benefit = Benefit.objects.create(
            range=range_obj, type='Percentage', value=D('10.00')
        )

        # Open Offer
        ConditionalOffer.objects.create(
            name='Open', slug='open',
            condition=condition, benefit=benefit, status='Open'
        )
        # Suspended Offer
        ConditionalOffer.objects.create(
            name='Suspended', slug='suspended',
            condition=condition, benefit=benefit, status='Suspended'
        )

    def test_nur_verfuegbare_offers(self):
        """Nur Open Offers werden zurückgegeben"""
        response = self.client.get('/api/offers/available/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'Open')


# ============================================================================
# WICHTIGE SCHNITTSTELLE: Offer Create
# ============================================================================

class TestOfferCreate(TestCase):
    """POST /api/offers/ - Offer erstellen"""

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
        """Erfolgreiche Offer-Erstellung"""
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
        """Validation Error bei fehlenden Daten"""
        response = self.client.post('/api/offers/', {
            'name': '',  # Leer!
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)