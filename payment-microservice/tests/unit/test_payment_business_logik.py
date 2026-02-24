
"""
UNIT TESTS - Payment Service
"""
import pytest
from decimal import Decimal as D
from unittest.mock import Mock

from payment.services import (
    PaymentCalculator,
    PaymentValidator,
    PaymentService
)



class TestPaymentCalculator:

    """Tests für die Berechnungen"""

    def test_balance_normal(self):

        calculator = PaymentCalculator()
        result = calculator.calculate_balance(D('100.00'), D('60.00'), D('10.00'))

        assert result == D('50.00')

    def test_balance_all_used(self):

        calculator = PaymentCalculator()
        result = calculator.calculate_balance(D('100.00'), D('100.00'), D('0.00'))

        assert result == D('0.00')

    def test_balance_with_none(self):

        calculator = PaymentCalculator()
        result = calculator.calculate_balance(None, None, None)

        assert result == D('0.00')

    def test_available_for_refund(self):

        calculator = PaymentCalculator()
        result = calculator.calculate_available_for_refund(D('100.00'), D('30.00'))

        assert result == D('70.00')

    def test_available_for_refund_nothing_refunded(self):

        calculator = PaymentCalculator()
        result = calculator.calculate_available_for_refund(D('100.00'), D('0.00'))

        assert result == D('100.00')


class TestPaymentValidator:

    """Tests für die Validierungen"""

    def test_amount_valid(self):

        validator = PaymentValidator()
        valid, error = validator.validate_amount(D('50.00'))

        assert valid is True
        assert error is None

    def test_amount_zero(self):

        validator = PaymentValidator()
        valid, error = validator.validate_amount(D('0.00'))

        assert valid is False
        assert error is not None

    def test_amount_negative(self):

        validator = PaymentValidator()
        valid, error = validator.validate_amount(D('-10.00'))

        assert valid is False

    def test_amount_none(self):

        validator = PaymentValidator()
        valid, error = validator.validate_amount(None)

        assert valid is False

    def test_can_debit_enough_balance(self):

        validator = PaymentValidator()
        valid, error = validator.can_debit(D('50.00'), D('100.00'))

        assert valid is True

    def test_can_debit_exact_balance(self):

        validator = PaymentValidator()
        valid, error = validator.can_debit(D('100.00'), D('100.00'))

        assert valid is True

    def test_can_debit_not_enough(self):

        validator = PaymentValidator()
        valid, error = validator.can_debit(D('100.00'), D('50.00'))

        assert valid is False
        assert 'Nicht genug Guthaben' in error

    def test_can_refund_available(self):

        validator = PaymentValidator()
        valid, error = validator.can_refund(D('50.00'), D('100.00'))

        assert valid is True

    def test_can_refund_too_much(self):

        validator = PaymentValidator()
        valid, error = validator.can_refund(D('50.00'), D('30.00'))

        assert valid is False



class TestPaymentService:

    """Tests für den Payment Service"""

    def test_payment_summary(self):

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

        service = PaymentService()
        valid, error = service.check_debit(D('50.00'), D('100.00'))

        assert valid is True

    def test_check_debit_not_ok(self):

        service = PaymentService()
        valid, error = service.check_debit(D('100.00'), D('50.00'))

        assert valid is False

    def test_check_refund_ok(self):

        service = PaymentService()
        valid, error = service.check_refund(D('50.00'), D('100.00'))

        assert valid is True

    def test_check_refund_not_ok(self):

        service = PaymentService()
        valid, error = service.check_refund(D('100.00'), D('50.00'))

        assert valid is False

    def test_hide_card_number(self):

        service = PaymentService()
        result = service.hide_card_number('1234567890123456')

        assert result == 'XXXX-XXXX-XXXX-3456'

    def test_hide_card_number_with_dashes(self):

        service = PaymentService()
        result = service.hide_card_number('1234-5678-9012-3456')

        assert result == 'XXXX-XXXX-XXXX-3456'

    def test_hide_card_number_already_hidden(self):

        service = PaymentService()
        result = service.hide_card_number('XXXX-XXXX-XXXX-1234')

        assert result == 'XXXX-XXXX-XXXX-1234'

    def test_hide_card_number_empty(self):

        service = PaymentService()
        result = service.hide_card_number('')

        assert result == ''

