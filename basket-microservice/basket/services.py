"""
Basket Service Layer
Business Logic getrennt von Models für bessere Testbarkeit
"""
from decimal import Decimal as D
from django.utils.timezone import now
from typing import Optional, Tuple


class BasketCalculator:
    """Berechnungen für Warenkorb und Warenkorbzeilen"""

    @staticmethod
    def calculate_line_price_excl_tax(price_excl_tax: Optional[D], quantity: int) -> D:
        """Zeilenpreis ohne Steuer berechnen"""
        if price_excl_tax is None or quantity <= 0:
            return D('0.00')
        return price_excl_tax * quantity

    @staticmethod
    def calculate_line_price_incl_tax(price_incl_tax: Optional[D], quantity: int) -> D:
        """Zeilenpreis mit Steuer berechnen"""
        if price_incl_tax is None or quantity <= 0:
            return D('0.00')
        return price_incl_tax * quantity

    @staticmethod
    def calculate_line_price_with_discount(line_price: D, discount: D) -> D:
        """Zeilenpreis nach Rabatt (nie negativ)"""
        if line_price is None or discount is None:
            return D('0.00')
        return max(D('0.00'), line_price - discount)

    @staticmethod
    def calculate_basket_total_excl_tax(lines: list) -> D:
        """Warenkorb-Gesamtsumme ohne Steuer"""
        total = D('0.00')
        for line in lines:
            if hasattr(line, 'price_excl_tax') and line.price_excl_tax:
                total += line.quantity * line.price_excl_tax
        return total

    @staticmethod
    def calculate_basket_total_incl_tax(lines: list) -> D:
        """Warenkorb-Gesamtsumme mit Steuer"""
        total = D('0.00')
        for line in lines:
            if hasattr(line, 'price_incl_tax') and line.price_incl_tax:
                total += line.quantity * line.price_incl_tax
        return total

    @staticmethod
    def calculate_basket_total_discount(lines: list) -> D:
        """Gesamt-Rabatt im Warenkorb"""
        total = D('0.00')
        for line in lines:
            if hasattr(line, 'discount_value') and line.discount_value:
                total += line.discount_value
        return total

    @staticmethod
    def calculate_num_items(lines: list) -> int:
        """Anzahl aller Artikel im Warenkorb"""
        return sum(line.quantity for line in lines if hasattr(line, 'quantity'))


class BasketValidator:
    """Validierungen für Warenkorb-Operationen"""

    OPEN = 'Open'
    SAVED = 'Saved'
    FROZEN = 'Frozen'
    MERGED = 'Merged'
    SUBMITTED = 'Submitted'

    EDITABLE_STATUSES = [OPEN, SAVED]

    @classmethod
    def can_be_edited(cls, status: str) -> bool:
        """Prüft ob Warenkorb bearbeitet werden kann"""
        return status in cls.EDITABLE_STATUSES

    @staticmethod
    def validate_quantity(quantity: int) -> bool:
        """Prüft ob Menge gültig ist"""
        return quantity is not None and quantity > 0

    @staticmethod
    def validate_price(price: Optional[D]) -> bool:
        """Prüft ob Preis gültig ist"""
        if price is None:
            return False
        return price >= D('0.00')

    @staticmethod
    def validate_product_id(product_id: Optional[int]) -> bool:
        """Prüft ob Produkt-ID gültig ist"""
        return product_id is not None and product_id > 0

    @classmethod
    def validate_basket_editable(cls, status: str) -> Tuple[bool, Optional[str]]:
        """Validiert ob Basket bearbeitet werden kann"""
        if not cls.can_be_edited(status):
            return False, f"Cannot modify a {status} basket"
        return True, None


class BasketService:
    """Haupt-Service für Warenkorb-Operationen"""

    def __init__(self):
        self.calculator = BasketCalculator()
        self.validator = BasketValidator()

    def calculate_totals(self, lines: list) -> dict:
        """Alle Warenkorb-Summen berechnen"""
        return {
            'total_excl_tax': self.calculator.calculate_basket_total_excl_tax(lines),
            'total_incl_tax': self.calculator.calculate_basket_total_incl_tax(lines),
            'total_discount': self.calculator.calculate_basket_total_discount(lines),
            'num_items': self.calculator.calculate_num_items(lines),
            'num_lines': len(lines)
        }

    def validate_add_product(
        self,
        basket_status: str,
        product_id: int,
        quantity: int,
        price_excl_tax: D
    ) -> Tuple[bool, Optional[str]]:
        """Validiert Produkt-Hinzufügen"""
        valid, error = self.validator.validate_basket_editable(basket_status)
        if not valid:
            return False, error

        if not self.validator.validate_product_id(product_id):
            return False, "Invalid product_id"

        if not self.validator.validate_quantity(quantity):
            return False, "Invalid quantity"

        if not self.validator.validate_price(price_excl_tax):
            return False, "Invalid price"

        return True, None

    def freeze_basket(self, current_status: str) -> Tuple[str, bool]:
        """Friert Basket ein"""
        if not self.validator.can_be_edited(current_status):
            return current_status, False
        return self.validator.FROZEN, True

    def thaw_basket(self, current_status: str) -> Tuple[str, bool]:
        """Taut Basket auf"""
        if current_status != self.validator.FROZEN:
            return current_status, False
        return self.validator.OPEN, True

    def submit_basket(self, current_status: str) -> Tuple[str, Optional[str], bool]:
        """Basket abschicken"""
        if not self.validator.can_be_edited(current_status):
            return current_status, None, False
        return self.validator.SUBMITTED, now().isoformat(), True

    def merge_line_quantities(self, existing_quantity: int, new_quantity: int) -> int:
        """Mengen beim Merge zusammenrechnen"""
        return existing_quantity + new_quantity

    def calculate_merge_status(self) -> Tuple[str, str]:
        """Status nach Merge"""
        return self.validator.MERGED, now().isoformat()
