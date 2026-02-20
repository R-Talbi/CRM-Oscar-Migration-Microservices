import django.utils.timezone
from decimal import Decimal as D
from django.db import models
from django.utils.timezone import now


class Basket(models.Model):
    """
    Oscar AbstractBasket - vollständig migriert.
    owner FK → customer_id (int)
    vouchers M2M → voucher_codes (JSON)
    """
    # Statt FK zu User → ID lokal!
    customer_id = models.IntegerField(null=True, blank=True)
    customer_email = models.EmailField(blank=True, default='')

    # Status wie Oscar!
    OPEN = 'Open'
    MERGED = 'Merged'
    SAVED = 'Saved'
    FROZEN = 'Frozen'
    SUBMITTED = 'Submitted'

    STATUS_CHOICES = [
        (OPEN, 'Open - currently active'),
        (MERGED, 'Merged - superceded by another basket'),
        (SAVED, 'Saved - for items to be purchased later'),
        (FROZEN, 'Frozen - cannot be modified'),
        (SUBMITTED, 'Submitted - has been ordered'),
    ]
    status = models.CharField(
        max_length=128,
        default=OPEN,
        choices=STATUS_CHOICES
    )

    # Voucher Codes lokal gespeichert statt M2M!
    voucher_codes = models.JSONField(default=list, blank=True)

    # Timestamps wie Oscar!
    date_created = models.DateTimeField(default=django.utils.timezone.now)
    date_merged = models.DateTimeField(null=True, blank=True)
    date_submitted = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return f"{self.status} basket (customer: {self.customer_id})"

    @property
    def is_empty(self):
        return self.lines.count() == 0

    @property
    def num_lines(self):
        return self.lines.count()

    @property
    def num_items(self):
        return sum(line.quantity for line in self.lines.all())

    @property
    def total_excl_tax(self):
        total = D('0.00')
        for line in self.lines.all():
            total += line.line_price_excl_tax
        return total

    @property
    def total_incl_tax(self):
        total = D('0.00')
        for line in self.lines.all():
            if line.price_incl_tax:
                total += line.quantity * line.price_incl_tax
        return total

    @property
    def total_discount(self):
        total = D('0.00')
        for line in self.lines.all():
            total += line.discount_value
        return total

    @property
    def can_be_edited(self):
        return self.status in (self.OPEN, self.SAVED)

    # Methoden wie Oscar!
    def freeze(self):
        self.status = self.FROZEN
        self.save()

    def thaw(self):
        self.status = self.OPEN
        self.save()

    def submit(self):
        self.status = self.SUBMITTED
        self.date_submitted = now()
        self.save()

    def merge(self, other_basket):
        """Zwei Baskets zusammenführen wie Oscar!"""
        for line in other_basket.lines.all():
            try:
                existing = self.lines.get(
                    product_id=line.product_id
                )
                existing.quantity += line.quantity
                existing.save()
                line.delete()
            except BasketLine.DoesNotExist:
                line.basket = self
                line.save()
        other_basket.status = self.MERGED
        other_basket.date_merged = now()
        other_basket.save()

    def add_product(self, product_id, product_title,
                    price_excl_tax, price_incl_tax,
                    quantity=1, currency='EUR'):
        """Produkt zum Basket hinzufügen wie Oscar!"""
        if not self.can_be_edited:
            raise PermissionError(
                f"Cannot modify a {self.status} basket"
            )
        try:
            line = self.lines.get(product_id=product_id)
            line.quantity += quantity
            line.save()
            return line, False
        except BasketLine.DoesNotExist:
            line = BasketLine.objects.create(
                basket=self,
                product_id=product_id,
                product_title=product_title,
                price_excl_tax=price_excl_tax,
                price_incl_tax=price_incl_tax,
                price_currency=currency,
                quantity=quantity
            )
            return line, True


class BasketLine(models.Model):
    """
    Oscar AbstractLine (Basket) - vollständig migriert.
    product FK → product_id + product_title + price (lokal!)
    stockrecord FK → stockrecord_id (int)
    """
    basket = models.ForeignKey(
        Basket,
        on_delete=models.CASCADE,
        related_name='lines'
    )

    # Line Reference wie Oscar!
    line_reference = models.SlugField(max_length=128, db_index=True, default='')

    # Statt FK zu catalogue.Product → Daten lokal!
    product_id = models.IntegerField()
    product_title = models.CharField(max_length=255, default='')

    # Statt FK zu partner.StockRecord → ID lokal!
    stockrecord_id = models.IntegerField(null=True, blank=True)

    quantity = models.PositiveIntegerField(default=1)

    # Preise wie Oscar!
    price_currency = models.CharField(max_length=12, default='EUR')
    price_excl_tax = models.DecimalField(
        decimal_places=2, max_digits=12, null=True
    )
    price_incl_tax = models.DecimalField(
        decimal_places=2, max_digits=12, null=True
    )
    tax_code = models.CharField(max_length=64, blank=True, null=True)

    # Discount wie Oscar!
    discount_value = models.DecimalField(
        decimal_places=2, max_digits=12, default=D('0.00')
    )

    # Offer Referenz
    offer_id = models.IntegerField(null=True, blank=True)

    date_created = models.DateTimeField(default=django.utils.timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date_created', 'pk']
        unique_together = ('basket', 'line_reference')

    def __str__(self):
        return f"Basket #{self.basket.id}, " \
               f"Product #{self.product_id}, " \
               f"qty {self.quantity}"

    def save(self, *args, **kwargs):
        if not self.basket.can_be_edited:
            raise PermissionError(
                f"Cannot modify a {self.basket.status} basket"
            )
        if not self.line_reference:
            self.line_reference = f"{self.basket.id}_{self.product_id}"
        super().save(*args, **kwargs)

    @property
    def line_price_excl_tax(self):
        if self.price_excl_tax:
            return self.quantity * self.price_excl_tax
        return D('0.00')

    @property
    def line_price_incl_tax(self):
        if self.price_incl_tax:
            return self.quantity * self.price_incl_tax
        return D('0.00')

    @property
    def line_price_excl_tax_incl_discounts(self):
        return max(D('0.00'), self.line_price_excl_tax - self.discount_value)

    @property
    def unit_price_excl_tax(self):
        return self.price_excl_tax

    @property
    def unit_price_incl_tax(self):
        return self.price_incl_tax


class BasketLineAttribute(models.Model):
    """
    Oscar AbstractLineAttribute (Basket) - vollständig migriert.
    """
    line = models.ForeignKey(
        BasketLine,
        on_delete=models.CASCADE,
        related_name='attributes'
    )
    # Statt FK zu catalogue.Option → Name lokal!
    option_name = models.CharField(max_length=128)
    value = models.JSONField()

    class Meta:
        verbose_name = 'Basket Line Attribute'

    def __str__(self):
        return f"{self.option_name} = {self.value}"
