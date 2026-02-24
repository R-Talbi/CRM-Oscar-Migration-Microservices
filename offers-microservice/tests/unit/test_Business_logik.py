
"""
UNIT TESTS - Zentrale Business Logic
"""
import pytest
from decimal import Decimal as D
from unittest.mock import Mock, patch
from datetime import datetime
from django.utils.timezone import make_aware

from offers.services import (
    DiscountCalculator,
    ConditionChecker,
    OfferApplicationService
)


class TestDiscountCalculation:

    """Tests für Rabatt Berechnung"""

    def test_percentage_discount_normal_case(self):
        calculator = DiscountCalculator()
        result = calculator.calculate_percentage_discount(D('100.00'), D('10.00'))
        assert result == D('10.00')

    def test_percentage_discount_50_percent(self):
        calculator = DiscountCalculator()
        result = calculator.calculate_percentage_discount(D('200.00'), D('50.00'))
        assert result == D('100.00')

    def test_fixed_discount_normal(self):
        calculator = DiscountCalculator()
        result = calculator.calculate_fixed_discount(D('100.00'), D('20.00'))
        assert result == D('20.00')

    def test_fixed_discount_exceeds_price(self):
        calculator = DiscountCalculator()
        result = calculator.calculate_fixed_discount(D('100.00'), D('150.00'))
        assert result == D('100.00')

    def test_multibuy_discount_two_items(self):
        calculator = DiscountCalculator()
        result = calculator.calculate_multibuy_discount(D('50.00'), 2)
        assert result == D('25.00')

    def test_discount_with_none_value(self):
        calculator = DiscountCalculator()
        result = calculator.calculate_percentage_discount(D('100.00'), None)
        assert result == D('0.00')

    def test_discount_with_zero_value(self):
        calculator = DiscountCalculator()
        result = calculator.calculate_fixed_discount(D('100.00'), D('0.00'))
        assert result == D('0.00')

    def test_multibuy_with_zero_quantity(self):
        calculator = DiscountCalculator()
        result = calculator.calculate_multibuy_discount(D('50.00'), 0)
        assert result == D('0.00')




class TestConditionChecking:

    """Tests für Condition Prüfung"""

    def test_count_condition_satisfied(self):
        checker = ConditionChecker()
        result = checker.check_count_condition(5, D('3'))
        assert result is True

    def test_count_condition_not_satisfied(self):
        checker = ConditionChecker()
        result = checker.check_count_condition(2, D('3'))
        assert result is False

    def test_count_condition_exactly_met(self):
        checker = ConditionChecker()
        result = checker.check_count_condition(3, D('3'))
        assert result is True

    def test_value_condition_satisfied(self):
        checker = ConditionChecker()
        result = checker.check_value_condition(D('100.00'), D('50.00'))
        assert result is True

    def test_value_condition_not_satisfied(self):
        checker = ConditionChecker()
        result = checker.check_value_condition(D('50.00'), D('100.00'))
        assert result is False

    def test_condition_with_none_value(self):
        checker = ConditionChecker()
        result = checker.check_count_condition(5, None)
        assert result is False



class TestOfferAvailability:

    """Tests für Offer-Verfügbarkeit"""

    def test_offer_available_open_status(self):
        service = OfferApplicationService()
        result = service.is_offer_available(
            status='Open',
            start_datetime=None,
            end_datetime=None,
            is_suspended_status='Suspended'
        )
        assert result is True

    def test_offer_not_available_suspended(self):
        service = OfferApplicationService()
        result = service.is_offer_available(
            status='Suspended',
            start_datetime=None,
            end_datetime=None,
            is_suspended_status='Suspended'
        )
        assert result is False

    @patch('offers.services.now')
    def test_offer_not_started_yet(self, mock_now):
        current = make_aware(datetime(2025, 1, 1, 12, 0))
        mock_now.return_value = current

        start = make_aware(datetime(2025, 1, 2, 12, 0))

        service = OfferApplicationService()
        result = service.is_offer_available(
            status='Open',
            start_datetime=start,
            end_datetime=None,
            is_suspended_status='Suspended'
        )
        assert result is False

    @patch('offers.services.now')
    def test_offer_already_ended(self, mock_now):
        current = make_aware(datetime(2025, 1, 10, 12, 0))
        mock_now.return_value = current

        end = make_aware(datetime(2025, 1, 5, 12, 0))

        service = OfferApplicationService()
        result = service.is_offer_available(
            status='Open',
            start_datetime=None,
            end_datetime=end,
            is_suspended_status='Suspended'
        )
        assert result is False

    @patch('offers.services.now')
    def test_offer_in_active_period(self, mock_now):
        current = make_aware(datetime(2025, 1, 5, 12, 0))
        mock_now.return_value = current

        start = make_aware(datetime(2025, 1, 1, 12, 0))
        end = make_aware(datetime(2025, 1, 10, 12, 0))

        service = OfferApplicationService()
        result = service.is_offer_available(
            status='Open',
            start_datetime=start,
            end_datetime=end,
            is_suspended_status='Suspended'
        )
        assert result is True


class TestBenefitAndCondition:

    """Tests für Zusammenspiel von Benefit und Condition"""

    def test_calculate_benefit_percentage(self):
        service = OfferApplicationService()
        result = service.calculate_benefit_discount(
            benefit_type='Percentage',
            benefit_value=D('15.00'),
            line_price=D('200.00'),
            quantity=1
        )
        assert result == D('30.00')

    def test_calculate_benefit_absolute(self):
        service = OfferApplicationService()
        result = service.calculate_benefit_discount(
            benefit_type='Absolute',
            benefit_value=D('25.00'),
            line_price=D('100.00'),
            quantity=1
        )
        assert result == D('25.00')

    def test_calculate_benefit_multibuy(self):
        service = OfferApplicationService()
        result = service.calculate_benefit_discount(
            benefit_type='Multibuy',
            benefit_value=None,
            line_price=D('60.00'),
            quantity=3
        )
        assert result == D('20.00')

    def test_condition_count_satisfied(self):
        service = OfferApplicationService()
        result = service.is_condition_satisfied(
            condition_type='Count',
            condition_value=D('2'),
            basket_total=D('100.00'),
            basket_quantity=3
        )
        assert result is True

    def test_condition_value_satisfied(self):
        service = OfferApplicationService()
        result = service.is_condition_satisfied(
            condition_type='Value',
            condition_value=D('75.00'),
            basket_total=D('100.00'),
            basket_quantity=2
        )
        assert result is True



class TestMaxDiscountLimits:

    """Tests für Max Discount"""

    def test_no_max_discount_limit(self):
        service = OfferApplicationService()
        result = service.apply_offer_with_limits(
            discount=D('50.00'),
            max_discount=None,
            total_discount=D('0.00')
        )
        assert result == D('50.00')

    def test_discount_under_limit(self):
        service = OfferApplicationService()
        result = service.apply_offer_with_limits(
            discount=D('30.00'),
            max_discount=D('100.00'),
            total_discount=D('50.00')
        )
        assert result == D('30.00')

    def test_discount_exceeds_limit(self):
        service = OfferApplicationService()
        result = service.apply_offer_with_limits(
            discount=D('50.00'),
            max_discount=D('100.00'),
            total_discount=D('90.00')
        )
        assert result == D('10.00')

    def test_discount_exactly_at_limit(self):
        service = OfferApplicationService()
        result = service.apply_offer_with_limits(
            discount=D('20.00'),
            max_discount=D('100.00'),
            total_discount=D('80.00')
        )
        assert result == D('20.00')


class TestCompleteOfferFlow:

    """Tests für kompletten Offer Flow"""

    def test_successful_offer_application(self):
        service = OfferApplicationService()

        # Offer verfügbar
        is_available = service.is_offer_available(
            status='Open',
            start_datetime=None,
            end_datetime=None,
            is_suspended_status='Suspended'
        )
        assert is_available is True

        # Condition erfüllt
        condition_met = service.is_condition_satisfied(
            condition_type='Value',
            condition_value=D('50.00'),
            basket_total=D('100.00'),
            basket_quantity=2
        )
        assert condition_met is True

        # Rabatt berechnen
        discount = service.calculate_benefit_discount(
            benefit_type='Percentage',
            benefit_value=D('10.00'),
            line_price=D('100.00'),
            quantity=2
        )
        assert discount == D('10.00')

    def test_failed_offer_condition_not_met(self):
        service = OfferApplicationService()

        condition_met = service.is_condition_satisfied(
            condition_type='Value',
            condition_value=D('100.00'),
            basket_total=D('30.00'),
            basket_quantity=1
        )
        assert condition_met is False

    def test_offer_with_max_discount_applied(self):
        service = OfferApplicationService()

        # Hoher Rabatt berechnet
        discount = service.calculate_benefit_discount(
            benefit_type='Percentage',
            benefit_value=D('50.00'),
            line_price=D('200.00'),
            quantity=1
        )
        assert discount == D('100.00')

        final_discount = service.apply_offer_with_limits(
            discount=discount,
            max_discount=D('75.00'),
            total_discount=D('0.00')
        )
        assert final_discount == D('75.00')
