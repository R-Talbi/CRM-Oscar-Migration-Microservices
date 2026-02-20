from django.db import models
from django.utils.timezone import now


class ShippingAddress(models.Model):
    """
    Oscar ShippingAddress - lokal gespeichert!
    Statt FK → Daten direkt im Order!
    """
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)
    line3 = models.CharField(max_length=255, blank=True)
    line4 = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    postcode = models.CharField(max_length=64, blank=True)
    country = models.CharField(max_length=128)
    phone_number = models.CharField(max_length=32, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Shipping Address'

    def __str__(self):
        return f"{self.line1}, {self.line4}"


class BillingAddress(models.Model):
    """Billing Adresse lokal gespeichert!"""
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)
    line4 = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    postcode = models.CharField(max_length=64, blank=True)
    country = models.CharField(max_length=128)

    class Meta:
        verbose_name = 'Billing Address'

    def __str__(self):
        return f"{self.line1}, {self.line4}"


class Order(models.Model):
    """
    Oscar AbstractOrder - vollständig migriert!
    Alle FKs durch IDs ersetzt!
    """
    # Order Nummer wie Oscar!
    number = models.CharField(max_length=128, db_index=True, unique=True)

    # Statt FK zu User → ID lokal!
    customer_id = models.IntegerField(null=True, blank=True)
    guest_email = models.EmailField(blank=True)

    # Statt FK zu basket.Basket → ID lokal!
    basket_id = models.IntegerField(null=True, blank=True)

    # Statt FK zu BillingAddress/ShippingAddress → Eigene Models!
    billing_address = models.ForeignKey(
        BillingAddress,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    shipping_address = models.ForeignKey(
        ShippingAddress,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    # Preise wie Oscar!
    currency = models.CharField(max_length=12, default='EUR')
    total_incl_tax = models.DecimalField(decimal_places=2, max_digits=12)
    total_excl_tax = models.DecimalField(decimal_places=2, max_digits=12)
    shipping_incl_tax = models.DecimalField(
        decimal_places=2, max_digits=12, default=0
    )
    shipping_excl_tax = models.DecimalField(
        decimal_places=2, max_digits=12, default=0
    )
    shipping_tax_code = models.CharField(max_length=64, blank=True, null=True)
    shipping_method = models.CharField(max_length=128, blank=True)
    shipping_code = models.CharField(max_length=128, blank=True)

    # Status wie Oscar!
    status = models.CharField(max_length=100, blank=True)

    date_placed = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ['-date_placed']

    def __str__(self):
        return f"#{self.number}"

    def save(self, *args, **kwargs):
        if not self.date_placed:
            self.date_placed = now()
        super().save(*args, **kwargs)

    @property
    def email(self):
        return self.guest_email

    @property
    def total_tax(self):
        return self.total_incl_tax - self.total_excl_tax

    @property
    def basket_total_incl_tax(self):
        return self.total_incl_tax - self.shipping_incl_tax

    @property
    def num_lines(self):
        return self.lines.count()

    @property
    def num_items(self):
        return sum(line.quantity for line in self.lines.all())

    def set_status(self, new_status):
        """Status setzen wie Oscar!"""
        old_status = self.status
        self.status = new_status
        self.save()
        # Status Change tracken!
        OrderStatusChange.objects.create(
            order=self,
            old_status=old_status,
            new_status=new_status
        )


class OrderLine(models.Model):
    """
    Oscar AbstractLine (Order) - vollständig migriert!
    product FK → product_id + title (lokal!)
    stockrecord FK → stockrecord_id (int)
    partner FK → partner_name (lokal!)
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='lines'
    )

    # Partner Info lokal gespeichert wie Oscar!
    partner_name = models.CharField(max_length=128, blank=True)
    partner_sku = models.CharField(max_length=128)
    partner_line_reference = models.CharField(max_length=128, blank=True)
    partner_line_notes = models.TextField(blank=True)

    # Statt FK zu partner.StockRecord → ID lokal!
    stockrecord_id = models.IntegerField(null=True, blank=True)

    # Statt FK zu catalogue.Product → Daten lokal!
    product_id = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=255)
    upc = models.CharField(max_length=128, blank=True, null=True)

    quantity = models.PositiveIntegerField(default=1)

    # Preise wie Oscar!
    line_price_incl_tax = models.DecimalField(decimal_places=2, max_digits=12)
    line_price_excl_tax = models.DecimalField(decimal_places=2, max_digits=12)
    line_price_before_discounts_incl_tax = models.DecimalField(
        decimal_places=2, max_digits=12
    )
    line_price_before_discounts_excl_tax = models.DecimalField(
        decimal_places=2, max_digits=12
    )
    unit_price_incl_tax = models.DecimalField(
        decimal_places=2, max_digits=12, blank=True, null=True
    )
    unit_price_excl_tax = models.DecimalField(
        decimal_places=2, max_digits=12, blank=True, null=True
    )
    tax_code = models.CharField(max_length=64, blank=True, null=True)

    status = models.CharField(max_length=255, blank=True)
    num_allocated = models.PositiveIntegerField(default=0)
    allocation_cancelled = models.BooleanField(default=False)

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return f"Product '{self.title}', qty {self.quantity}"

    @property
    def discount_incl_tax(self):
        return (self.line_price_before_discounts_incl_tax
                - self.line_price_incl_tax)

    @property
    def discount_excl_tax(self):
        return (self.line_price_before_discounts_excl_tax
                - self.line_price_excl_tax)


class OrderLineAttribute(models.Model):
    """Oscar AbstractLineAttribute (Order) - vollständig migriert!"""
    line = models.ForeignKey(
        OrderLine,
        on_delete=models.CASCADE,
        related_name='attributes'
    )
    # Statt FK zu catalogue.Option → Name lokal!
    option_name = models.CharField(max_length=128)
    type = models.CharField(max_length=128)
    value = models.JSONField()

    def __str__(self):
        return f"{self.type} = {self.value}"


class OrderStatusChange(models.Model):
    """Oscar AbstractOrderStatusChange - vollständig migriert!"""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_changes'
    )
    old_status = models.CharField(max_length=100, blank=True)
    new_status = models.CharField(max_length=100, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return f"Order {self.order} from {self.old_status} to {self.new_status}"


class OrderNote(models.Model):
    """Oscar AbstractOrderNote - vollständig migriert!"""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='notes'
    )
    # Statt FK zu User → ID lokal!
    customer_id = models.IntegerField(null=True, blank=True)

    INFO = 'Info'
    WARNING = 'Warning'
    ERROR = 'Error'
    SYSTEM = 'System'

    NOTE_TYPES = [
        (INFO, 'Info'),
        (WARNING, 'Warning'),
        (ERROR, 'Error'),
        (SYSTEM, 'System'),
    ]
    note_type = models.CharField(max_length=128, blank=True)
    message = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_updated']

    def __str__(self):
        return f"'{self.message[:50]}'"


class OrderDiscount(models.Model):
    """Oscar AbstractOrderDiscount - vollständig migriert!"""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='discounts'
    )

    BASKET = 'Basket'
    SHIPPING = 'Shipping'
    DEFERRED = 'Deferred'

    CATEGORY_CHOICES = [
        (BASKET, 'Basket'),
        (SHIPPING, 'Shipping'),
        (DEFERRED, 'Deferred'),
    ]
    category = models.CharField(
        max_length=64,
        default=BASKET,
        choices=CATEGORY_CHOICES
    )
    # Offer Referenz (Offers Microservice über Kong!)
    offer_id = models.PositiveIntegerField(blank=True, null=True)
    offer_name = models.CharField(max_length=128, db_index=True, blank=True)
    voucher_id = models.PositiveIntegerField(blank=True, null=True)
    voucher_code = models.CharField(max_length=128, db_index=True, blank=True)
    frequency = models.PositiveIntegerField(null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=12, default=0)
    message = models.TextField(blank=True)

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return f"Discount of {self.amount} from order {self.order}"