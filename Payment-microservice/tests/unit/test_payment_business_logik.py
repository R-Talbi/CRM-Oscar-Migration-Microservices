"""
UNIT TESTS - Payment Service
Einfache Tests für die wichtigsten Funktionen
Von: Student/Junior Developer
"""
import pytest
from decimal import Decimal as D
from unittest.mock import Mock

from payment.services import (
    PaymentCalculator,
    PaymentValidator,
    PaymentService
)


# ============================================================================
# TESTS FÜR CALCULATOR (Berechnungen)
# ============================================================================

class TestPaymentCalculator:
    """Tests für die Berechnungen"""

    def test_balance_normal(self):
        """
        Test: Normaler Balance
        Allocated 100 - Debited 60 + Refunded 10 = 50
        """
        calculator = PaymentCalculator()
        result = calculator.calculate_balance(D('100.00'), D('60.00'), D('10.00'))

        # Prüfen ob richtig
        assert result == D('50.00')

    def test_balance_all_used(self):
        """
        Test: Alles wurde abgebucht
        Allocated 100 - Debited 100 = 0
        """
        calculator = PaymentCalculator()
        result = calculator.calculate_balance(D('100.00'), D('100.00'), D('0.00'))

        assert result == D('0.00')

    def test_balance_with_none(self):
        """
        Test: Was wenn Werte None sind?
        Sollte 0 zurückgeben
        """
        calculator = PaymentCalculator()
        result = calculator.calculate_balance(None, None, None)

        assert result == D('0.00')

    def test_available_for_refund(self):
        """
        Test: Wie viel kann zurückerstattet werden?
        Debited 100 - Refunded 30 = 70 verfügbar
        """
        calculator = PaymentCalculator()
        result = calculator.calculate_available_for_refund(D('100.00'), D('30.00'))

        assert result == D('70.00')

    def test_available_for_refund_nothing_refunded(self):
        """
        Test: Noch nichts zurückerstattet
        Debited 100 - Refunded 0 = 100 verfügbar
        """
        calculator = PaymentCalculator()
        result = calculator.calculate_available_for_refund(D('100.00'), D('0.00'))

        assert result == D('100.00')


# ============================================================================
# TESTS FÜR VALIDATOR (Prüfungen)
# ============================================================================

class TestPaymentValidator:
    """Tests für die Validierungen"""

    def test_amount_valid(self):
        """
        Test: Gültiger Betrag (50€)
        Sollte OK sein
        """
        validator = PaymentValidator()
        valid, error = validator.validate_amount(D('50.00'))

        assert valid is True
        assert error is None

    def test_amount_zero(self):
        """
        Test: Betrag ist 0
        Sollte NICHT OK sein
        """
        validator = PaymentValidator()
        valid, error = validator.validate_amount(D('0.00'))

        assert valid is False
        assert error is not None

    def test_amount_negative(self):
        """
        Test: Negativer Betrag (-10€)
        Sollte NICHT OK sein
        """
        validator = PaymentValidator()
        valid, error = validator.validate_amount(D('-10.00'))

        assert valid is False

    def test_amount_none(self):
        """
        Test: Betrag ist None
        Sollte NICHT OK sein
        """
        validator = PaymentValidator()
        valid, error = validator.validate_amount(None)

        assert valid is False

    def test_can_debit_enough_balance(self):
        """
        Test: Debit mit genug Guthaben
        Balance 100, Amount 50 → OK
        """
        validator = PaymentValidator()
        valid, error = validator.can_debit(D('50.00'), D('100.00'))

        assert valid is True

    def test_can_debit_exact_balance(self):
        """
        Test: Debit mit genau richtigem Guthaben
        Balance 100, Amount 100 → OK
        """
        validator = PaymentValidator()
        valid, error = validator.can_debit(D('100.00'), D('100.00'))

        assert valid is True

    def test_can_debit_not_enough(self):
        """
        Test: Debit mit zu wenig Guthaben
        Balance 50, Amount 100 → NICHT OK
        """
        validator = PaymentValidator()
        valid, error = validator.can_debit(D('100.00'), D('50.00'))

        assert valid is False
        assert 'Nicht genug Guthaben' in error

    def test_can_refund_available(self):
        """
        Test: Refund möglich
        Available 100, Amount 50 → OK
        """
        validator = PaymentValidator()
        valid, error = validator.can_refund(D('50.00'), D('100.00'))

        assert valid is True

    def test_can_refund_too_much(self):
        """
        Test: Refund zu viel
        Available 30, Amount 50 → NICHT OK
        """
        validator = PaymentValidator()
        valid, error = validator.can_refund(D('50.00'), D('30.00'))

        assert valid is False


# ============================================================================
# TESTS FÜR SERVICE (Haupt-Funktionen)
# ============================================================================

class TestPaymentService:
    """Tests für den Payment Service"""

    def test_payment_summary(self):
        """
        Test: Komplette Zusammenfassung
        Sollte alle Werte richtig zurückgeben
        """
        service = PaymentService()

        result = service.get_payment_summary(
            allocated=D('100.00'),
            debited=D('60.00'),
            refunded=D('10.00')
        )

        # Alle Werte prüfen
        assert result['allocated'] == D('100.00')
        assert result['debited'] == D('60.00')
        assert result['refunded'] == D('10.00')
        assert result['balance'] == D('50.00')  # 100 - 60 + 10
        assert result['available_for_refund'] == D('50.00')  # 60 - 10

    def test_check_debit_ok(self):
        """
        Test: Debit prüfen - OK
        """
        service = PaymentService()
        valid, error = service.check_debit(D('50.00'), D('100.00'))

        assert valid is True

    def test_check_debit_not_ok(self):
        """
        Test: Debit prüfen - NICHT OK
        """
        service = PaymentService()
        valid, error = service.check_debit(D('100.00'), D('50.00'))

        assert valid is False

    def test_check_refund_ok(self):
        """
        Test: Refund prüfen - OK
        """
        service = PaymentService()
        valid, error = service.check_refund(D('50.00'), D('100.00'))

        assert valid is True

    def test_check_refund_not_ok(self):
        """
        Test: Refund prüfen - NICHT OK
        """
        service = PaymentService()
        valid, error = service.check_refund(D('100.00'), D('50.00'))

        assert valid is False

    def test_hide_card_number(self):
        """
        Test: Kartennummer verstecken
        1234567890123456 → XXXX-XXXX-XXXX-3456
        """
        service = PaymentService()
        result = service.hide_card_number('1234567890123456')

        assert result == 'XXXX-XXXX-XXXX-3456'

    def test_hide_card_number_with_dashes(self):
        """
        Test: Kartennummer mit Bindestrichen
        1234-5678-9012-3456 → XXXX-XXXX-XXXX-3456
        """
        service = PaymentService()
        result = service.hide_card_number('1234-5678-9012-3456')

        assert result == 'XXXX-XXXX-XXXX-3456'

    def test_hide_card_number_already_hidden(self):
        """
        Test: Schon versteckte Nummer
        Sollte gleich bleiben
        """
        service = PaymentService()
        result = service.hide_card_number('XXXX-XXXX-XXXX-1234')

        assert result == 'XXXX-XXXX-XXXX-1234'

    def test_hide_card_number_empty(self):
        """
        Test: Leere Kartennummer
        Sollte leer bleiben
        """
        service = PaymentService()
        result = service.hide_card_number('')

        assert result == ''

