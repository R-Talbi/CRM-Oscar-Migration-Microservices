
"""
UNIT TESTS - Orders Service Zentrale Business Logic
"""
import pytest
from decimal import Decimal as D
from unittest.mock import Mock

from orders.services import (
    OrderCalculator,
    OrderValidator,
    OrderService
)



class TestOrderStatusTransitions:
    """Tests für Order Status Übergänge"""

    def test_status_transition_pending_to_processing(self):
        validator = OrderValidator()
        valid, error = validator.validate_status_transition('Pending', 'Processing')
        assert valid is True
        assert error is None

    def test_status_transition_pending_to_cancelled(self):
        validator = OrderValidator()
        valid, error = validator.validate_status_transition('Pending', 'Cancelled')
        assert valid is True

    def test_status_transition_pending_to_shipped_not_allowed(self):
        validator = OrderValidator()
        valid, error = validator.validate_status_transition('Pending', 'Shipped')
        assert valid is False
        assert 'Cannot transition' in error

    def test_status_transition_processing_to_shipped(self):
        validator = OrderValidator()
        valid, error = validator.validate_status_transition('Processing', 'Shipped')
        assert valid is True

    def test_status_transition_processing_to_cancelled(self):
        validator = OrderValidator()
        valid, error = validator.validate_status_transition('Processing', 'Cancelled')
        assert valid is True

    def test_status_transition_shipped_to_delivered(self):
        validator = OrderValidator()
        valid, error = validator.validate_status_transition('Shipped', 'Delivered')
        assert valid is True

    def test_status_transition_delivered_to_refunded(self):
        validator = OrderValidator()
        valid, error = validator.validate_status_transition('Delivered', 'Refunded')
        assert valid is True

    def test_status_transition_cancelled_is_final(self):
        validator = OrderValidator()
        valid, error = validator.validate_status_transition('Cancelled', 'Processing')
        assert valid is False

    def test_can_cancel_pending(self):
        validator = OrderValidator()
        assert validator.can_cancel('Pending') is True

    def test_can_cancel_shipped_not_allowed(self):
        validator = OrderValidator()
        assert validator.can_cancel('Shipped') is False

    def test_can_ship_processing(self):
        validator = OrderValidator()
        assert validator.can_ship('Processing') is True

    def test_can_ship_pending_not_allowed(self):
        validator = OrderValidator()
        assert validator.can_ship('Pending') is False

    def test_can_refund_delivered(self):
        validator = OrderValidator()
        assert validator.can_refund('Delivered') is True

    def test_can_refund_pending_not_allowed(self):
        validator = OrderValidator()
        assert validator.can_refund('Pending') is False



class TestOrderOperations:

    """Tests für Order-Operationen"""

    def test_cancel_order_success(self):
        service = OrderService()
        new_status, success, error = service.cancel_order('Pending')

        assert new_status == 'Cancelled'
        assert success is True
        assert error is None

    def test_cancel_order_not_allowed(self):
        service = OrderService()
        new_status, success, error = service.cancel_order('Shipped')

        assert new_status == 'Shipped'  # Bleibt unverändert
        assert success is False
        assert error is not None

    def test_ship_order_success(self):
        service = OrderService()
        new_status, success, error = service.ship_order('Processing')

        assert new_status == 'Shipped'
        assert success is True

    def test_ship_order_not_allowed(self):
        service = OrderService()
        new_status, success, error = service.ship_order('Pending')

        assert success is False

    def test_deliver_order_success(self):
        service = OrderService()
        new_status, success, error = service.deliver_order('Shipped')

        assert new_status == 'Delivered'
        assert success is True

    def test_refund_order_success(self):
        service = OrderService()
        new_status, success, error = service.refund_order('Delivered')

        assert new_status == 'Refunded'
        assert success is True



class TestOrderValidation:

    """Tests Validierung für Order-Erstellung"""

    def test_validate_order_creation_with_customer(self):
        service = OrderService()
        line = Mock()

        valid, error = service.validate_order_creation(
            customer_id=42,
            guest_email='',
            total_incl_tax=D('100.00'),
            total_excl_tax=D('84.00'),
            lines=[line]
        )

        assert valid is True
        assert error is None

    def test_validate_order_creation_with_guest_email(self):
        service = OrderService()
        line = Mock()

        valid, error = service.validate_order_creation(
            customer_id=None,
            guest_email='guest@example.com',
            total_incl_tax=D('100.00'),
            total_excl_tax=D('84.00'),
            lines=[line]
        )

        assert valid is True

    def test_validate_order_creation_no_customer(self):
        service = OrderService()

        valid, error = service.validate_order_creation(
            customer_id=None,
            guest_email='',
            total_incl_tax=D('100.00'),
            total_excl_tax=D('84.00'),
            lines=[Mock()]
        )

        assert valid is False
        assert 'required' in error

    def test_validate_order_creation_no_lines(self):
        service = OrderService()

        valid, error = service.validate_order_creation(
            customer_id=42,
            guest_email='',
            total_incl_tax=D('100.00'),
            total_excl_tax=D('84.00'),
            lines=[]
        )

        assert valid is False
        assert 'line' in error

    def test_validate_email_valid(self):
        validator = OrderValidator()
        valid, error = validator.validate_email('test@example.com')
        assert valid is True

    def test_validate_email_invalid(self):
        validator = OrderValidator()
        valid, error = validator.validate_email('invalid-email')
        assert valid is False



class TestOrderCalculations:

    """Tests für Order Berechnung"""

    def test_calculate_order_total(self):
        calculator = OrderCalculator()

        line1 = Mock()
        line1.line_price_excl_tax = D('50.00')
        line1.line_price_incl_tax = D('59.50')

        line2 = Mock()
        line2.line_price_excl_tax = D('30.00')
        line2.line_price_incl_tax = D('35.70')

        result = calculator.calculate_order_total(
            [line1, line2],
            shipping=D('5.00')
        )

        assert result['total_excl_tax'] == D('80.00')
        assert result['total_incl_tax'] == D('95.20')
        assert result['grand_total'] == D('100.20')  # 95.20 + 5

    def test_calculate_total_tax(self):
        calculator = OrderCalculator()
        result = calculator.calculate_total_tax(D('119.00'), D('100.00'))
        assert result == D('19.00')

    def test_calculate_num_items(self):
        calculator = OrderCalculator()

        line1 = Mock()
        line1.quantity = 2

        line2 = Mock()
        line2.quantity = 3

        result = calculator.calculate_num_items([line1, line2])
        assert result == 5

    def test_calculate_order_summary(self):
        service = OrderService()

        line = Mock()
        line.line_price_excl_tax = D('100.00')
        line.line_price_incl_tax = D('119.00')
        line.quantity = 2

        discount = Mock()
        discount.amount = D('10.00')

        result = service.calculate_order_summary(
            lines=[line],
            shipping=D('5.00'),
            discounts=[discount]
        )

        assert result['total_excl_tax'] == D('100.00')
        assert result['total_incl_tax'] == D('119.00')
        assert result['total_tax'] == D('19.00')
        assert result['shipping_incl_tax'] == D('5.00')
        assert result['total_discount'] == D('10.00')
        assert result['grand_total'] == D('114.00')  # 119 + 5 - 10
        assert result['num_items'] == 2
