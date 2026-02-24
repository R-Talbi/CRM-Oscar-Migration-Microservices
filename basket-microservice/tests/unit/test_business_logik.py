"""
UNIT TESTS - Basket Service Business Logic
"""

import pytest
from decimal import Decimal as D
from unittest.mock import Mock
from datetime import datetime

from basket.services import (
    BasketCalculator,
    BasketValidator,
    BasketService
)

class TestBasketCalculator:

    """Tests für Basket Berechnungen"""

    def test_calculate_line_price_excl_tax_normal(self):
        calculator = BasketCalculator()
        result = calculator.calculate_line_price_excl_tax(D('10.00'), 2)
        assert result == D('20.00')

    def test_calculate_line_price_excl_tax_single_item(self):
        calculator = BasketCalculator()
        result = calculator.calculate_line_price_excl_tax(D('50.00'), 1)
        assert result == D('50.00')

    def test_calculate_line_price_excl_tax_zero_quantity(self):
        calculator = BasketCalculator()
        result = calculator.calculate_line_price_excl_tax(D('10.00'), 0)
        assert result == D('0.00')

    def test_calculate_line_price_excl_tax_none_price(self):
        calculator = BasketCalculator()
        result = calculator.calculate_line_price_excl_tax(None, 5)
        assert result == D('0.00')

    def test_calculate_line_price_incl_tax(self):
        calculator = BasketCalculator()
        result = calculator.calculate_line_price_incl_tax(D('11.90'), 3)
        assert result == D('35.70')

    def test_calculate_line_price_with_discount(self):
        calculator = BasketCalculator()
        result = calculator.calculate_line_price_with_discount(D('100.00'), D('15.00'))
        assert result == D('85.00')

    def test_calculate_line_price_with_discount_never_negative(self):
        calculator = BasketCalculator()
        result = calculator.calculate_line_price_with_discount(D('50.00'), D('100.00'))
        assert result == D('0.00')

    def test_calculate_line_price_with_discount_none_values(self):
        calculator = BasketCalculator()
        result = calculator.calculate_line_price_with_discount(None, D('10.00'))
        assert result == D('0.00')

    def test_calculate_basket_total_excl_tax(self):
        calculator = BasketCalculator()

        line1 = Mock()
        line1.price_excl_tax = D('10.00')
        line1.quantity = 3

        line2 = Mock()
        line2.price_excl_tax = D('25.00')
        line2.quantity = 2

        result = calculator.calculate_basket_total_excl_tax([line1, line2])
        assert result == D('80.00')

    def test_calculate_basket_total_incl_tax(self):
        calculator = BasketCalculator()

        line1 = Mock()
        line1.price_incl_tax = D('11.90')
        line1.quantity = 2

        line2 = Mock()
        line2.price_incl_tax = D('29.90')
        line2.quantity = 1

        result = calculator.calculate_basket_total_incl_tax([line1, line2])
        assert result == D('53.70')

    def test_calculate_basket_total_discount(self):
        calculator = BasketCalculator()

        line1 = Mock()
        line1.discount_value = D('5.00')

        line2 = Mock()
        line2.discount_value = D('10.00')

        result = calculator.calculate_basket_total_discount([line1, line2])
        assert result == D('15.00')

    def test_calculate_num_items(self):
        calculator = BasketCalculator()

        line1 = Mock()
        line1.quantity = 3

        line2 = Mock()
        line2.quantity = 2

        line3 = Mock()
        line3.quantity = 1

        result = calculator.calculate_num_items([line1, line2, line3])
        assert result == 6

    def test_calculate_basket_total_empty_basket(self):
        calculator = BasketCalculator()
        result = calculator.calculate_basket_total_excl_tax([])
        assert result == D('0.00')


class TestBasketValidator:

    """Tests für Basket Validierung"""

    def test_can_be_edited_open_status(self):
        validator = BasketValidator()
        result = validator.can_be_edited('Open')
        assert result is True

    def test_can_be_edited_saved_status(self):
        validator = BasketValidator()
        result = validator.can_be_edited('Saved')
        assert result is True

    def test_can_be_edited_frozen_status(self):
        validator = BasketValidator()
        result = validator.can_be_edited('Frozen')
        assert result is False

    def test_can_be_edited_submitted_status(self):
        validator = BasketValidator()
        result = validator.can_be_edited('Submitted')
        assert result is False

    def test_validate_quantity_valid(self):
        validator = BasketValidator()
        result = validator.validate_quantity(5)
        assert result is True

    def test_validate_quantity_zero(self):
        validator = BasketValidator()
        result = validator.validate_quantity(0)
        assert result is False

    def test_validate_quantity_negative(self):
        validator = BasketValidator()
        result = validator.validate_quantity(-5)
        assert result is False

    def test_validate_quantity_none(self):
        validator = BasketValidator()
        result = validator.validate_quantity(None)
        assert result is False

    def test_validate_price_valid(self):
        validator = BasketValidator()
        result = validator.validate_price(D('50.00'))
        assert result is True

    def test_validate_price_zero(self):
        validator = BasketValidator()
        result = validator.validate_price(D('0.00'))
        assert result is True

    def test_validate_price_negative(self):
        validator = BasketValidator()
        result = validator.validate_price(D('-10.00'))
        assert result is False

    def test_validate_price_none(self):
        validator = BasketValidator()
        result = validator.validate_price(None)
        assert result is False

    def test_validate_product_id_valid(self):
        validator = BasketValidator()
        result = validator.validate_product_id(123)
        assert result is True

    def test_validate_product_id_zero(self):
        validator = BasketValidator()
        result = validator.validate_product_id(0)
        assert result is False

    def test_validate_product_id_none(self):
        validator = BasketValidator()
        result = validator.validate_product_id(None)
        assert result is False

    def test_validate_basket_editable_open(self):
        validator = BasketValidator()
        valid, error = validator.validate_basket_editable('Open')
        assert valid is True
        assert error is None

    def test_validate_basket_editable_frozen(self):
        validator = BasketValidator()
        valid, error = validator.validate_basket_editable('Frozen')
        assert valid is False
        assert error == "Cannot modify a Frozen basket"



class TestBasketService:

    """Tests für Basket-Service Anwendung"""

    def test_calculate_totals(self):
        service = BasketService()

        line1 = Mock()
        line1.price_excl_tax = D('10.00')
        line1.price_incl_tax = D('11.90')
        line1.discount_value = D('2.00')
        line1.quantity = 2

        line2 = Mock()
        line2.price_excl_tax = D('50.00')
        line2.price_incl_tax = D('59.50')
        line2.discount_value = D('5.00')
        line2.quantity = 1

        result = service.calculate_totals([line1, line2])

        assert result['total_excl_tax'] == D('70.00')  # 20 + 50
        assert result['total_incl_tax'] == D('83.30')  # 23.80 + 59.50
        assert result['total_discount'] == D('7.00')  # 2 + 5
        assert result['num_items'] == 3  # 2 + 1
        assert result['num_lines'] == 2

    def test_validate_add_product_success(self):
        service = BasketService()
        valid, error = service.validate_add_product(
            basket_status='Open',
            product_id=123,
            quantity=2,
            price_excl_tax=D('50.00')
        )
        assert valid is True
        assert error is None

    def test_validate_add_product_frozen_basket(self):
        service = BasketService()
        valid, error = service.validate_add_product(
            basket_status='Frozen',
            product_id=123,
            quantity=2,
            price_excl_tax=D('50.00')
        )
        assert valid is False
        assert error == "Cannot modify a Frozen basket"

    def test_validate_add_product_invalid_quantity(self):
        service = BasketService()
        valid, error = service.validate_add_product(
            basket_status='Open',
            product_id=123,
            quantity=0,  # Ungültig!
            price_excl_tax=D('50.00')
        )
        assert valid is False
        assert error == "Invalid quantity"

    def test_validate_add_product_invalid_price(self):
        service = BasketService()
        valid, error = service.validate_add_product(
            basket_status='Open',
            product_id=123,
            quantity=2,
            price_excl_tax=D('-10.00')  # Negativ!
        )
        assert valid is False
        assert error == "Invalid price"

    def test_freeze_basket_from_open(self):
        service = BasketService()
        new_status, success = service.freeze_basket('Open')
        assert new_status == 'Frozen'
        assert success is True

    def test_freeze_basket_already_frozen(self):
        service = BasketService()
        new_status, success = service.freeze_basket('Frozen')
        assert new_status == 'Frozen'
        assert success is False

    def test_thaw_basket_from_frozen(self):
        service = BasketService()
        new_status, success = service.thaw_basket('Frozen')
        assert new_status == 'Open'
        assert success is True

    def test_thaw_basket_not_frozen(self):
        service = BasketService()
        new_status, success = service.thaw_basket('Open')
        assert new_status == 'Open'
        assert success is False

    def test_submit_basket_from_open(self):
        service = BasketService()
        new_status, timestamp, success = service.submit_basket('Open')
        assert new_status == 'Submitted'
        assert timestamp is not None
        assert success is True

    def test_submit_basket_already_submitted(self):
        service = BasketService()
        new_status, timestamp, success = service.submit_basket('Submitted')
        assert new_status == 'Submitted'
        assert timestamp is None
        assert success is False

    def test_merge_line_quantities(self):
        service = BasketService()
        result = service.merge_line_quantities(3, 2)
        assert result == 5

    def test_calculate_merge_status(self):
        service = BasketService()
        status, timestamp = service.calculate_merge_status()
        assert status == 'Merged'
        assert timestamp is not None