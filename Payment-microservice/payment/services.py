"""
Payment Service Layer
Einfache Business Logic für Payment-Operationen
Von: Student/Junior Developer
"""
from decimal import Decimal as D


class PaymentCalculator:
    """
    Einfache Berechnungen für Payments
    """

    def calculate_balance(self, allocated, debited, refunded):
        """
        Berechnet das aktuelle Guthaben

        Formel: Balance = Allocated - Debited + Refunded

        Beispiel:
        - Allocated: 100€ (reserviert)
        - Debited: 60€ (abgebucht)
        - Refunded: 10€ (zurückerstattet)
        → Balance: 50€
        """
        # Wenn Werte None sind, auf 0 setzen
        if allocated is None:
            allocated = D('0.00')
        if debited is None:
            debited = D('0.00')
        if refunded is None:
            refunded = D('0.00')

        # Einfache Formel
        balance = allocated - debited + refunded
        return balance

    def calculate_available_for_refund(self, debited, refunded):
        """
        Wie viel kann zurückerstattet werden?

        Man kann nur zurückerstatten was schon abgebucht wurde
        """
        if debited is None:
            debited = D('0.00')
        if refunded is None:
            refunded = D('0.00')

        available = debited - refunded
        return available


class PaymentValidator:
    """
    Einfache Prüfungen für Payments
    """

    def validate_amount(self, amount):
        """
        Prüft ob der Betrag gültig ist

        Regeln:
        - Muss vorhanden sein (nicht None)
        - Muss positiv sein (größer als 0)
        """
        # Ist der Betrag None?
        if amount is None:
            return False, "Betrag fehlt"

        # Ist der Betrag negativ oder 0?
        if amount <= D('0.00'):
            return False, "Betrag muss größer als 0 sein"

        # Alles OK!
        return True, None

    def can_debit(self, amount, balance):
        """
        Kann ich diesen Betrag abbuchen?

        Regel: Man kann nur abbuchen was verfügbar ist
        """
        # Erst Betrag prüfen
        valid, error = self.validate_amount(amount)
        if not valid:
            return False, error

        # Balance checken
        if balance is None:
            balance = D('0.00')

        # Nicht genug Guthaben?
        if amount > balance:
            return False, f"Nicht genug Guthaben. Verfügbar: {balance}, Benötigt: {amount}"

        # Alles OK!
        return True, None

    def can_refund(self, amount, available):
        """
        Kann ich diesen Betrag zurückerstatten?

        Regel: Man kann nur zurückerstatten was abgebucht wurde
        """
        # Erst Betrag prüfen
        valid, error = self.validate_amount(amount)
        if not valid:
            return False, error

        # Available checken
        if available is None:
            available = D('0.00')

        # Zu viel?
        if amount > available:
            return False, f"Kann nicht {amount} zurückerstatten. Verfügbar: {available}"

        # Alles OK!
        return True, None


class PaymentService:
    """
    Haupt-Service für Payment-Operationen
    Nutzt Calculator und Validator
    """

    def __init__(self):
        # Wir brauchen einen Calculator und einen Validator
        self.calculator = PaymentCalculator()
        self.validator = PaymentValidator()

    def get_payment_summary(self, allocated, debited, refunded):
        """
        Gibt eine Zusammenfassung zurück

        Was kommt raus:
        - Allocated (reserviert)
        - Debited (abgebucht)
        - Refunded (zurückerstattet)
        - Balance (aktuelles Guthaben)
        - Available for Refund (was kann zurückerstattet werden)
        """
        # Balance berechnen
        balance = self.calculator.calculate_balance(allocated, debited, refunded)

        # Available for Refund berechnen
        available = self.calculator.calculate_available_for_refund(debited, refunded)

        # Alles zusammenpacken
        summary = {
            'allocated': allocated,
            'debited': debited,
            'refunded': refunded,
            'balance': balance,
            'available_for_refund': available
        }

        return summary

    def check_debit(self, amount, balance):
        """
        Prüft ob Debit erlaubt ist

        Gibt zurück: (erlaubt?, fehler_text)
        """
        return self.validator.can_debit(amount, balance)

    def check_refund(self, amount, available):
        """
        Prüft ob Refund erlaubt ist

        Gibt zurück: (erlaubt?, fehler_text)
        """
        return self.validator.can_refund(amount, available)

    def hide_card_number(self, card_number):
        """
        Versteckt die Kartennummer aus Sicherheitsgründen

        Vorher: 1234567890123456
        Nachher: XXXX-XXXX-XXXX-3456

        Nur die letzten 4 Ziffern bleiben sichtbar
        """
        # Ist die Nummer leer?
        if not card_number:
            return ""

        # Ist sie schon versteckt?
        if card_number.startswith('X'):
            return card_number

        # Nur Zahlen behalten (keine Bindestriche etc.)
        numbers = ''.join(c for c in card_number if c.isdigit())

        # Zu kurz?
        if len(numbers) < 4:
            return "XXXX-XXXX-XXXX-XXXX"

        # Letzte 4 Ziffern holen
        last_four = numbers[-4:]

        # Versteckte Nummer erstellen
        hidden = f"XXXX-XXXX-XXXX-{last_four}"

        return hidden

