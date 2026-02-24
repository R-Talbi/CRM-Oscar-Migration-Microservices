

# Payment Service Layer

from decimal import Decimal as D


class PaymentCalculator:

    def calculate_balance(self, allocated, debited, refunded):

        if allocated is None:
            allocated = D('0.00')
        if debited is None:
            debited = D('0.00')
        if refunded is None:
            refunded = D('0.00')

        balance = allocated - debited + refunded
        return balance

    def calculate_available_for_refund(self, debited, refunded):

        if debited is None:
            debited = D('0.00')
        if refunded is None:
            refunded = D('0.00')

        available = debited - refunded
        return available


class PaymentValidator:

    def validate_amount(self, amount):

        if amount is None:
            return False, "Betrag fehlt"

        if amount <= D('0.00'):
            return False, "Betrag muss größer als 0 sein"

        return True, None

    def can_debit(self, amount, balance):

        valid, error = self.validate_amount(amount)
        if not valid:
            return False, error

        if balance is None:
            balance = D('0.00')

        if amount > balance:
            return False, f"Nicht genug Guthaben. Verfügbar: {balance}, Benötigt: {amount}"

        return True, None

    def can_refund(self, amount, available):

        valid, error = self.validate_amount(amount)
        if not valid:
            return False, error

        if available is None:
            available = D('0.00')

        if amount > available:
            return False, f"Kann nicht {amount} zurückerstatten. Verfügbar: {available}"

        return True, None


class PaymentService:

    def __init__(self):
        self.calculator = PaymentCalculator()
        self.validator = PaymentValidator()

    def get_payment_summary(self, allocated, debited, refunded):
        balance = self.calculator.calculate_balance(allocated, debited, refunded)

        available = self.calculator.calculate_available_for_refund(debited, refunded)

        summary = {
            'allocated': allocated,
            'debited': debited,
            'refunded': refunded,
            'balance': balance,
            'available_for_refund': available
        }

        return summary

    def check_debit(self, amount, balance):

        return self.validator.can_debit(amount, balance)

    def check_refund(self, amount, available):

        return self.validator.can_refund(amount, available)

    def hide_card_number(self, card_number):

        if not card_number:
            return ""

        if card_number.startswith('X'):
            return card_number

        numbers = ''.join(c for c in card_number if c.isdigit())

        if len(numbers) < 4:
            return "XXXX-XXXX-XXXX-XXXX"

        last_four = numbers[-4:]

        hidden = f"XXXX-XXXX-XXXX-{last_four}"

        return hidden

