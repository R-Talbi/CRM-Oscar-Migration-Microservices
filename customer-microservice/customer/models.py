from django.db import models


class Customer(models.Model):
    """
    Customer Model - migriert von Oscar User Modul.
    Speichert Kundendaten unabhängig vom Monolith.
    """

    # Basis Informationen
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)

    # Oscar spezifische Felder
    date_of_birth = models.DateField(null=True, blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.username} ({self.email})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class CustomerAddress(models.Model):
    """Adresse eines Kunden"""

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='addresses'
    )

    # Adresse
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    postcode = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    # Standard Adresse?
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_default']

    def __str__(self):
        return f"{self.line1}, {self.city}"