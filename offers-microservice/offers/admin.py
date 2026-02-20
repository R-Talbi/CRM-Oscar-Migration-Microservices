from django.contrib import admin
from .models import ConditionalOffer, Benefit, Condition, Range


@admin.register(ConditionalOffer)
class ConditionalOfferAdmin(admin.ModelAdmin):
    list_display = ["name", "offer_type", "status", "priority", "is_available", "num_applications"]
    list_filter = ["status", "offer_type"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Benefit)
class BenefitAdmin(admin.ModelAdmin):
    list_display = ["__str__", "type", "value"]


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ["__str__", "type", "value"]


@admin.register(Range)
class RangeAdmin(admin.ModelAdmin):
    list_display = ["name", "includes_all_products", "date_created"]
    prepopulated_fields = {"slug": ("name",)}
