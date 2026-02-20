"""
UNIT TESTS - Orders Service ZENTRALE Business Logic
Fokus auf das WICHTIGSTE: Status-Transitions + Order-Validierung + Berechnungen
"""
import pytest
from decimal import Decimal as D
from unittest.mock import Mock

from orders.services import (
    OrderCalculator,
    OrderValidator,
    OrderService
)

# ============================================================================
# KERN-LOGIK: STATUS-TRANSITIONS (Das WICHTIGSTE bei Orders!)
# ============================================================================

class TestOrderStatusTransitions:
    """Tests für Order Status-Übergänge - KERNFUNKTION!"""

    def test_status_transition_pending_to_processing(self):
        """✅ Erlaubt: Pending → Processing"""
        validator = OrderValidator()
        valid, error = validator.validate_status_transition('Pending', 'Processing')
        assert valid is True
        assert error is None

    def test_status_transition_pending_to_cancelled(self):
        """✅ Erlaubt: Pending → Cancelled"""
        validator = OrderValidator()
        valid, error = validator.validate_status_transition('Pending', 'Cancelled')
        assert valid is True

    def test_status_transition_pending_to_shipped_not_allowed(self):
        """❌ NICHT erlaubt: Pending → Shipped (muss erst Processing sein!)"""
        validator = OrderValidator()
        valid, error = validator.validate_status_transition('Pending', 'Shipped')
        assert valid is False
        assert 'Cannot transition' in error

    def test_status_transition_processing_to_shipped(self):
        """✅ Erlaubt: Processing → Shipped"""
        validator = OrderValidator()
        valid, error = validator.validate_status_transition('Processing', 'Shipped')
        assert valid is True

    def test_status_transition_processing_to_cancelled(self):
        """✅ Erlaubt: Processing → Cancelled"""
        validator = OrderValidator()
        valid, error = validator.validate_status_transition('Processing', 'Cancelled')
        assert valid is True

    def test_status_transition_shipped_to_delivered(self):
        """✅ Erlaubt: Shipped → Delivered"""
        validator = OrderValidator()
        valid, error = validator.validate_status_transition('Shipped', 'Delivered')
        assert valid is True

    def test_status_transition_delivered_to_refunded(self):
        """✅ Erlaubt: Delivered → Refunded"""
        validator = OrderValidator()
        valid, error = validator.validate_status_transition('Delivered', 'Refunded')
        assert valid is True

    def test_status_transition_cancelled_is_final(self):
        """❌ Cancelled ist FINAL - keine weiteren Transitions"""
        validator = OrderValidator()
        valid, error = validator.validate_status_transition('Cancelled', 'Processing')
        assert valid is False

    def test_can_cancel_pending(self):
        """Order in Pending kann storniert werden"""
        validator = OrderValidator()
        assert validator.can_cancel('Pending') is True

    def test_can_cancel_shipped_not_allowed(self):
        """Order in Shipped kann NICHT storniert werden"""
        validator = OrderValidator()
        assert validator.can_cancel('Shipped') is False

    def test_can_ship_processing(self):
        """Order in Processing kann verschickt werden"""
        validator = OrderValidator()
        assert validator.can_ship('Processing') is True

    def test_can_ship_pending_not_allowed(self):
        """Order in Pending kann NICHT verschickt werden"""
        validator = OrderValidator()
        assert validator.can_ship('Pending') is False

    def test_can_refund_delivered(self):
        """Order in Delivered kann zurückerstattet werden"""
        validator = OrderValidator()
        assert validator.can_refund('Delivered') is True

    def test_can_refund_pending_not_allowed(self):
        """Order in Pending kann NICHT zurückerstattet werden"""
        validator = OrderValidator()
        assert validator.can_refund('Pending') is False


# ============================================================================
# KERN-LOGIK: ORDER OPERATIONS
# ============================================================================

class TestOrderOperations:
    """Tests für Order-Operationen - cancel, ship, deliver, refund"""

    def test_cancel_order_success(self):
        """Order stornieren von Pending → Cancelled"""
        service = OrderService()
        new_status, success, error = service.cancel_order('Pending')

        assert new_status == 'Cancelled'
        assert success is True
        assert error is None

    def test_cancel_order_not_allowed(self):
        """Order stornieren von Shipped → Fehler"""
        service = OrderService()
        new_status, success, error = service.cancel_order('Shipped')

        assert new_status == 'Shipped'  # Bleibt unverändert
        assert success is False
        assert error is not None

    def test_ship_order_success(self):
        """Order verschicken von Processing → Shipped"""
        service = OrderService()
        new_status, success, error = service.ship_order('Processing')

        assert new_status == 'Shipped'
        assert success is True

    def test_ship_order_not_allowed(self):
        """Order verschicken von Pending → Fehler"""
        service = OrderService()
        new_status, success, error = service.ship_order('Pending')

        assert success is False

    def test_deliver_order_success(self):
        """Order ausgeliefert von Shipped → Delivered"""
        service = OrderService()
        new_status, success, error = service.deliver_order('Shipped')

        assert new_status == 'Delivered'
        assert success is True

    def test_refund_order_success(self):
        """Order zurückerstatten von Delivered → Refunded"""
        service = OrderService()
        new_status, success, error = service.refund_order('Delivered')

        assert new_status == 'Refunded'
        assert success is True


# ============================================================================
# KERN-LOGIK: ORDER VALIDIERUNG
# ============================================================================

class TestOrderValidation:
    """Tests für Order-Erstellung Validierung"""

    def test_validate_order_creation_with_customer(self):
        """Order mit customer_id ist gültig"""
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
        """Order mit guest_email ist gültig"""
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
        """FEHLER: Weder customer_id noch guest_email"""
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
        """FEHLER: Order ohne Lines"""
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
        """Gültige Email: test@example.com"""
        validator = OrderValidator()
        valid, error = validator.validate_email('test@example.com')
        assert valid is True

    def test_validate_email_invalid(self):
        """Ungültige Email: kein @"""
        validator = OrderValidator()
        valid, error = validator.validate_email('invalid-email')
        assert valid is False


# ============================================================================
# KERN-LOGIK: BERECHNUNGEN
# ============================================================================

class TestOrderCalculations:
    """Tests für Order-Berechnungen"""

    def test_calculate_order_total(self):
        """Order Total mit Lines + Shipping berechnen"""
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
        """Steuer berechnen: 119€ - 100€ = 19€"""
        calculator = OrderCalculator()
        result = calculator.calculate_total_tax(D('119.00'), D('100.00'))
        assert result == D('19.00')

    def test_calculate_num_items(self):
        """Anzahl Items: 2 + 3 = 5 Stück"""
        calculator = OrderCalculator()

        line1 = Mock()
        line1.quantity = 2

        line2 = Mock()
        line2.quantity = 3

        result = calculator.calculate_num_items([line1, line2])
        assert result == 5

    def test_calculate_order_summary(self):
        """Komplette Order Summary mit allem"""
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
