from decimal import Decimal as D
from django.db import models


class Range(models.Model):

    # Produkt ID lokal gespeichert statt FK


    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length=128, unique=True)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    includes_all_products = models.BooleanField(default=False)

    included_product_ids = models.JSONField(default=list, blank=True)
    excluded_product_ids = models.JSONField(default=list, blank=True)

    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def contains_product(self, product_id):
        if self.includes_all_products:
            return product_id not in self.excluded_product_ids
        return product_id in self.included_product_ids

    def add_product(self, product_id):
        if product_id not in self.included_product_ids:
            self.included_product_ids.append(product_id)
            self.save()

    def remove_product(self, product_id):
        if product_id in self.included_product_ids:
            self.included_product_ids.remove(product_id)
            self.excluded_product_ids.append(product_id)
            self.save()


class Benefit(models.Model):

    PERCENTAGE = "Percentage"
    FIXED = "Absolute"
    FIXED_UNIT = "Fixed"
    MULTIBUY = "Multibuy"
    FIXED_PRICE = "Fixed price"
    SHIPPING_PERCENTAGE = "Shipping percentage"
    SHIPPING_ABSOLUTE = "Shipping absolute"
    SHIPPING_FIXED_PRICE = "Shipping fixed price"

    TYPE_CHOICES = [
        (PERCENTAGE, "Discount is a percentage off of the product value"),
        (FIXED, "Discount is a fixed amount off of the basket total"),
        (FIXED_UNIT, "Discount is a fixed amount off of the product value"),
        (MULTIBUY, "Cheapest product for free"),
        (FIXED_PRICE, "Products for a fixed price"),
        (SHIPPING_ABSOLUTE, "Fixed amount off shipping"),
        (SHIPPING_FIXED_PRICE, "Fixed price shipping"),
        (SHIPPING_PERCENTAGE, "Percentage off shipping"),
    ]

    range = models.ForeignKey(Range, blank=True, null=True, on_delete=models.CASCADE)
    type = models.CharField(max_length=128, choices=TYPE_CHOICES, blank=True)
    value = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    max_affected_items = models.PositiveIntegerField(null=True, blank=True)
    proxy_class = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "Benefit"

    def __str__(self):
        return f"{self.type} - {self.value}"

    def apply_discount(self, line_price, quantity):
        if self.type == self.PERCENTAGE and self.value:
            return line_price * (self.value / 100)
        elif self.type == self.FIXED and self.value:
            return min(self.value, line_price)
        elif self.type == self.MULTIBUY:
            # Günstigstes Produkt gratis
            return line_price / quantity if quantity > 0 else D("0.00")
        return D("0.00")


class Condition(models.Model):

    COUNT = "Count"
    VALUE = "Value"
    COVERAGE = "Coverage"

    TYPE_CHOICES = [
        (COUNT, "Depends on number of items in basket"),
        (VALUE, "Depends on value of items in basket"),
        (COVERAGE, "Needs distinct items from range"),
    ]

    range = models.ForeignKey(Range, blank=True, null=True, on_delete=models.CASCADE)
    type = models.CharField(max_length=128, choices=TYPE_CHOICES, blank=True)
    value = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    proxy_class = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "Condition"

    def __str__(self):
        return f"{self.type} - {self.value}"

    def is_satisfied(self, basket_total, basket_quantity):
        if self.type == self.COUNT and self.value:
            return basket_quantity >= self.value
        elif self.type == self.VALUE and self.value:
            return basket_total >= self.value
        return False


class ConditionalOffer(models.Model):

    SITE = "Site"
    VOUCHER = "Voucher"
    USER = "User"
    SESSION = "Session"

    TYPE_CHOICES = [
        (SITE, "Site offer - available to all users"),
        (VOUCHER, "Voucher offer - only with voucher code"),
        (USER, "User offer - available to certain users"),
        (SESSION, "Session offer - temporary offer"),
    ]

    OPEN = "Open"
    SUSPENDED = "Suspended"
    CONSUMED = "Consumed"

    STATUS_CHOICES = [
        (OPEN, "Open"),
        (SUSPENDED, "Suspended"),
        (CONSUMED, "Consumed"),
    ]

    # Basis Felder wie Oscar

    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length=128, unique=True)
    description = models.TextField(blank=True)
    offer_type = models.CharField(max_length=128, choices=TYPE_CHOICES, default=SITE)
    exclusive = models.BooleanField(default=True)
    status = models.CharField(max_length=64, choices=STATUS_CHOICES, default=OPEN)

    # Verbindungen zu Benefit und Condition

    condition = models.ForeignKey(Condition, on_delete=models.CASCADE, related_name="offers")
    benefit = models.ForeignKey(Benefit, on_delete=models.CASCADE, related_name="offers")

    # Priorität

    priority = models.IntegerField(default=0, db_index=True)

    # Verfügbarkeit

    start_datetime = models.DateTimeField(blank=True, null=True)
    end_datetime = models.DateTimeField(blank=True, null=True)

    # Limits

    max_global_applications = models.PositiveIntegerField(null=True, blank=True)
    max_user_applications = models.PositiveIntegerField(null=True, blank=True)
    max_basket_applications = models.PositiveIntegerField(null=True, blank=True)
    max_discount = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)

    # Tracking
    total_discount = models.DecimalField(decimal_places=2, max_digits=12, default=D("0.00"))
    num_applications = models.PositiveIntegerField(default=0)
    num_orders = models.PositiveIntegerField(default=0)

    redirect_url = models.URLField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-priority", "pk"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):

        if not self.is_suspended:
            if (
                self.max_global_applications
                and self.num_applications >= self.max_global_applications
            ):
                self.status = self.CONSUMED
            else:
                self.status = self.OPEN
        super().save(*args, **kwargs)

    @property
    def is_open(self):
        return self.status == self.OPEN

    @property
    def is_suspended(self):
        return self.status == self.SUSPENDED

    def is_available(self):
        from django.utils.timezone import now

        if self.is_suspended:
            return False
        test_date = now()
        if self.start_datetime and self.start_datetime > test_date:
            return False
        if self.end_datetime and test_date > self.end_datetime:
            return False
        return True

    def record_usage(self, discount_amount):

        self.num_applications += 1
        self.total_discount += discount_amount
        self.num_orders += 1
        self.save()

    def apply_to_basket(self, basket_total, basket_quantity):

        if not self.is_available():
            return D("0.00")

        if not self.condition.is_satisfied(basket_total, basket_quantity):
            return D("0.00")

        discount = self.benefit.apply_discount(basket_total, basket_quantity)
        if self.max_discount:
            remaining = self.max_discount - self.total_discount
            discount = min(discount, remaining)
        if discount > 0:
            self.record_usage(discount)

        return discount
