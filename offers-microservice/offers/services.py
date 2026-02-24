
"""
Offers Service Layer
"""

from decimal import Decimal as D
from typing import Optional
from django.utils.timezone import now


class DiscountCalculator:

    # B. Logik für Rabatt Berechnung

    @staticmethod
    def calculate_percentage_discount(line_price: D, percentage: D) -> D:

        # Rabatt berechnen
        if not percentage or percentage <= 0:
            return D("0.00")
        return line_price * (percentage / 100)

    @staticmethod
    def calculate_fixed_discount(line_price: D, fixed_amount: D) -> D:
        if not fixed_amount or fixed_amount <= 0:
            return D("0.00")
        return min(fixed_amount, line_price)

    @staticmethod
    def calculate_multibuy_discount(line_price: D, quantity: int) -> D:

        if quantity <= 0:
            return D("0.00")
        return line_price / quantity


class ConditionChecker:

    # B. Logik für Condition Prüfung

    @staticmethod
    def check_count_condition(basket_quantity: int, required_count: D) -> bool:
        if not required_count:
            return False
        return basket_quantity >= required_count

    @staticmethod
    def check_value_condition(basket_total: D, required_value: D) -> bool:
        if not required_value:
            return False
        return basket_total >= required_value


class OfferApplicationService:

    # Haupt logik für Offers-Anwendung

    def __init__(self):
        self.discount_calculator = DiscountCalculator()
        self.condition_checker = ConditionChecker()

    def is_offer_available(
        self,
        status: str,
        start_datetime: Optional,
        end_datetime: Optional,
        is_suspended_status: str,
    ) -> bool:

        if status == is_suspended_status:
            return False

        current_time = now()

        if start_datetime and start_datetime > current_time:
            return False

        if end_datetime and current_time > end_datetime:
            return False

        return True

    def calculate_benefit_discount(
        self, benefit_type: str, benefit_value: Optional[D], line_price: D, quantity: int
    ) -> D:

        # Berechnung Rabatt

        if benefit_type == "Percentage" and benefit_value:
            return self.discount_calculator.calculate_percentage_discount(line_price, benefit_value)
        elif benefit_type == "Absolute" and benefit_value:
            return self.discount_calculator.calculate_fixed_discount(line_price, benefit_value)
        elif benefit_type == "Multibuy":
            return self.discount_calculator.calculate_multibuy_discount(line_price, quantity)
        return D("0.00")

    def is_condition_satisfied(
        self,
        condition_type: str,
        condition_value: Optional[D],
        basket_total: D,
        basket_quantity: int,
    ) -> bool:

        # Condition erfüllt oder nicht

        if condition_type == "Count" and condition_value:
            return self.condition_checker.check_count_condition(basket_quantity, condition_value)
        elif condition_type == "Value" and condition_value:
            return self.condition_checker.check_value_condition(basket_total, condition_value)
        return False

    def apply_offer_with_limits(
        self, discount: D, max_discount: Optional[D], total_discount: D
    ) -> D:

        # Max Discount

        if max_discount:
            remaining = max_discount - total_discount
            return min(discount, remaining, discount)
        return discount
