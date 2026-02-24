
"""
Orders Service Layer
Business Logic getrennt von Models für bessere Testbarkeit
"""
from decimal import Decimal as D
from typing import Optional, Tuple, Dict


class OrderCalculator:

    """Berechnungen für Orders"""

    @staticmethod
    def calculate_total_tax(total_incl_tax: D, total_excl_tax: D) -> D:
        if total_incl_tax is None or total_excl_tax is None:
            return D('0.00')
        return total_incl_tax - total_excl_tax

    @staticmethod
    def calculate_basket_total_incl_tax(
        total_incl_tax: D,
        shipping_incl_tax: D
    ) -> D:
        if total_incl_tax is None or shipping_incl_tax is None:
            return D('0.00')
        return total_incl_tax - shipping_incl_tax

    @staticmethod
    def calculate_line_discount_incl_tax(
        price_before_discount: D,
        price_after_discount: D
    ) -> D:
        if price_before_discount is None or price_after_discount is None:
            return D('0.00')
        return price_before_discount - price_after_discount

    @staticmethod
    def calculate_line_discount_excl_tax(
        price_before_discount: D,
        price_after_discount: D
    ) -> D:
        if price_before_discount is None or price_after_discount is None:
            return D('0.00')
        return price_before_discount - price_after_discount

    @staticmethod
    def calculate_num_lines(lines: list) -> int:
        return len(lines) if lines else 0

    @staticmethod
    def calculate_num_items(lines: list) -> int:
        if not lines:
            return 0
        return sum(
            line.quantity for line in lines
            if hasattr(line, 'quantity')
        )

    @staticmethod
    def calculate_order_total(lines: list, shipping: D = D('0.00')) -> Dict[str, D]:
        total_excl_tax = D('0.00')
        total_incl_tax = D('0.00')

        for line in lines:
            if hasattr(line, 'line_price_excl_tax') and line.line_price_excl_tax:
                total_excl_tax += line.line_price_excl_tax
            if hasattr(line, 'line_price_incl_tax') and line.line_price_incl_tax:
                total_incl_tax += line.line_price_incl_tax

        return {
            'total_excl_tax': total_excl_tax,
            'total_incl_tax': total_incl_tax,
            'shipping_incl_tax': shipping,
            'grand_total': total_incl_tax + shipping
        }

    @staticmethod
    def calculate_total_discount(discounts: list) -> D:
        if not discounts:
            return D('0.00')
        return sum(
            discount.amount for discount in discounts
            if hasattr(discount, 'amount') and discount.amount
        )


class OrderValidator:

    """Validierungen für Order Operations"""

    PENDING = 'Pending'
    PROCESSING = 'Processing'
    SHIPPED = 'Shipped'
    DELIVERED = 'Delivered'
    CANCELLED = 'Cancelled'
    REFUNDED = 'Refunded'

    VALID_STATUSES = [
        PENDING, PROCESSING, SHIPPED, DELIVERED, CANCELLED, REFUNDED
    ]

    ALLOWED_TRANSITIONS = {
        PENDING: [PROCESSING, CANCELLED],
        PROCESSING: [SHIPPED, CANCELLED],
        SHIPPED: [DELIVERED, REFUNDED],
        DELIVERED: [REFUNDED],
        CANCELLED: [],
        REFUNDED: []
    }

    @classmethod
    def validate_status(cls, status: str) -> Tuple[bool, Optional[str]]:
        if not status:
            return False, "Status is required"
        if status not in cls.VALID_STATUSES:
            return False, f"Invalid status: {status}"
        return True, None

    @classmethod
    def validate_status_transition(
        cls,
        old_status: str,
        new_status: str
    ) -> Tuple[bool, Optional[str]]:
        if old_status not in cls.VALID_STATUSES:
            return False, f"Invalid current status: {old_status}"

        if new_status not in cls.VALID_STATUSES:
            return False, f"Invalid new status: {new_status}"

        if old_status == new_status:
            return False, "Status unchanged"

        allowed = cls.ALLOWED_TRANSITIONS.get(old_status, [])
        if new_status not in allowed:
            return False, f"Cannot transition from {old_status} to {new_status}"

        return True, None

    @staticmethod
    def validate_total(total: D) -> Tuple[bool, Optional[str]]:
        if total is None:
            return False, "Total is required"
        if total < D('0.00'):
            return False, "Total cannot be negative"
        return True, None

    @staticmethod
    def validate_quantity(quantity: int) -> Tuple[bool, Optional[str]]:
        if quantity is None:
            return False, "Quantity is required"
        if quantity <= 0:
            return False, "Quantity must be positive"
        return True, None

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        if not email:
            return False, "Email is required"
        if '@' not in email:
            return False, "Invalid email format"
        return True, None

    @classmethod
    def can_cancel(cls, status: str) -> bool:
        return status in [cls.PENDING, cls.PROCESSING]

    @classmethod
    def can_ship(cls, status: str) -> bool:
        return status == cls.PROCESSING

    @classmethod
    def can_refund(cls, status: str) -> bool:
        return status in [cls.SHIPPED, cls.DELIVERED]


class OrderService:

    """Haupt logik für Order Operation"""

    def __init__(self):
        self.calculator = OrderCalculator()
        self.validator = OrderValidator()

    def calculate_order_summary(
        self,
        lines: list,
        shipping: D = D('0.00'),
        discounts: list = None
    ) -> Dict:
        totals = self.calculator.calculate_order_total(lines, shipping)

        total_discount = D('0.00')
        if discounts:
            total_discount = self.calculator.calculate_total_discount(discounts)

        return {
            'num_lines': self.calculator.calculate_num_lines(lines),
            'num_items': self.calculator.calculate_num_items(lines),
            'total_excl_tax': totals['total_excl_tax'],
            'total_incl_tax': totals['total_incl_tax'],
            'total_tax': self.calculator.calculate_total_tax(
                totals['total_incl_tax'],
                totals['total_excl_tax']
            ),
            'shipping_incl_tax': shipping,
            'total_discount': total_discount,
            'grand_total': totals['grand_total'] - total_discount
        }

    def validate_order_creation(
        self,
        customer_id: Optional[int],
        guest_email: str,
        total_incl_tax: D,
        total_excl_tax: D,
        lines: list
    ) -> Tuple[bool, Optional[str]]:

        if not customer_id and not guest_email:
            return False, "Either customer_id or guest_email required"

        if guest_email and not customer_id:
            valid, error = self.validator.validate_email(guest_email)
            if not valid:
                return False, error

        valid, error = self.validator.validate_total(total_incl_tax)
        if not valid:
            return False, error

        if not lines or len(lines) == 0:
            return False, "Order must have at least one line"

        return True, None

    def change_status(
        self,
        current_status: str,
        new_status: str
    ) -> Tuple[str, bool, Optional[str]]:
        valid, error = self.validator.validate_status_transition(
            current_status,
            new_status
        )

        if not valid:
            return current_status, False, error

        return new_status, True, None

    def cancel_order(
        self,
        current_status: str
    ) -> Tuple[str, bool, Optional[str]]:
        if not self.validator.can_cancel(current_status):
            return current_status, False, f"Cannot cancel order with status {current_status}"

        return self.validator.CANCELLED, True, None

    def ship_order(
        self,
        current_status: str
    ) -> Tuple[str, bool, Optional[str]]:
        if not self.validator.can_ship(current_status):
            return current_status, False, f"Cannot ship order with status {current_status}"

        return self.validator.SHIPPED, True, None

    def deliver_order(
        self,
        current_status: str
    ) -> Tuple[str, bool, Optional[str]]:

        valid, error = self.validator.validate_status_transition(
            current_status,
            self.validator.DELIVERED
        )

        if not valid:
            return current_status, False, error

        return self.validator.DELIVERED, True, None

    def refund_order(
        self,
        current_status: str
    ) -> Tuple[str, bool, Optional[str]]:

        if not self.validator.can_refund(current_status):
            return current_status, False, f"Cannot refund order with status {current_status}"

        return self.validator.REFUNDED, True, None

    def calculate_line_discount(
        self,
        price_before: D,
        price_after: D,
        include_tax: bool = True
    ) -> D:

        if include_tax:
            return self.calculator.calculate_line_discount_incl_tax(
                price_before, price_after
            )
        return self.calculator.calculate_line_discount_excl_tax(
            price_before, price_after
        )
