from decimal import Decimal as D
from django.db import models
from django.utils.translation import gettext_lazy as _


class SourceType(models.Model):
    """
    Oscar AbstractSourceType - vollständig migriert!
    z.B. PayPal, Kreditkarte, Banküberweisung
    """
    name = models.CharField(max_length=128, db_index=True)
    code = models.SlugField(max_length=128, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Source(models.Model):
    """
    Oscar AbstractSource - vollständig migriert!
    order FK → order_id (int)
    source_type FK → SourceType (lokal!)
    """
    # Statt FK zu order.Order → ID lokal!
    order_id = models.IntegerField()
    order_number = models.CharField(max_length=128)

    source_type = models.ForeignKey(
        SourceType,
        on_delete=models.CASCADE,
        related_name='sources'
    )

    currency = models.CharField(max_length=12, default='EUR')

    # Beträge wie Oscar!
    amount_allocated = models.DecimalField(
        decimal_places=2, max_digits=12, default=D('0.00')
    )
    amount_debited = models.DecimalField(
        decimal_places=2, max_digits=12, default=D('0.00')
    )
    amount_refunded = models.DecimalField(
        decimal_places=2, max_digits=12, default=D('0.00')
    )

    reference = models.CharField(max_length=255, blank=True)
    label = models.CharField(max_length=128, blank=True)

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return f"Allocation of {self.amount_allocated} from {self.source_type}"

    # Methoden wie Oscar!
    def allocate(self, amount, reference='', status=''):
        """Betrag reservieren wie Oscar!"""
        self.amount_allocated += amount
        self.save()
        self.transactions.create(
            txn_type=Transaction.AUTHORISE,
            amount=amount,
            reference=reference,
            status=status
        )

    def debit(self, amount=None, reference='', status=''):
        """Betrag abbuchen wie Oscar!"""
        if amount is None:
            amount = self.balance
        self.amount_debited += amount
        self.save()
        self.transactions.create(
            txn_type=Transaction.DEBIT,
            amount=amount,
            reference=reference,
            status=status
        )

    def refund(self, amount, reference='', status=''):
        """Rückerstattung wie Oscar!"""
        self.amount_refunded += amount
        self.save()
        self.transactions.create(
            txn_type=Transaction.REFUND,
            amount=amount,
            reference=reference,
            status=status
        )

    @property
    def balance(self):
        """Guthaben wie Oscar!"""
        return (self.amount_allocated
                - self.amount_debited
                + self.amount_refunded)

    @property
    def amount_available_for_refund(self):
        return self.amount_debited - self.amount_refunded


class Transaction(models.Model):
    """
    Oscar AbstractTransaction - vollständig migriert!
    """
    source = models.ForeignKey(
        Source,
        on_delete=models.CASCADE,
        related_name='transactions'
    )

    # Typen wie Oscar!
    AUTHORISE = 'Authorise'
    DEBIT = 'Debit'
    REFUND = 'Refund'

    TXN_TYPES = [
        (AUTHORISE, 'Authorise'),
        (DEBIT, 'Debit'),
        (REFUND, 'Refund'),
    ]
    txn_type = models.CharField(max_length=128, blank=True)
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    reference = models.CharField(max_length=128, blank=True)
    status = models.CharField(max_length=128, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return f"{self.txn_type} of {self.amount}"


class Bankcard(models.Model):
    """
    Oscar AbstractBankcard - vollständig migriert!
    user FK → customer_id (int)
    """
    # Statt FK zu User → ID lokal!
    customer_id = models.IntegerField()

    card_type = models.CharField(max_length=128)
    name = models.CharField(max_length=255, blank=True)

    # Nur letzte 4 Stellen wie Oscar!
    number = models.CharField(max_length=32)
    expiry_date = models.DateField()
    partner_reference = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Bankcard'

    def __str__(self):
        return f"{self.card_type} {self.number}"

    def save(self, *args, **kwargs):
        # Karte anonymisieren wie Oscar!
        if not self.number.startswith('X'):
            self.number = f"XXXX-XXXX-XXXX-{self.number[-4:]}"
        super().save(*args, **kwargs)

    @property
    def obfuscated_number(self):
        return f"XXXX-XXXX-XXXX-{self.number[-4:]}"