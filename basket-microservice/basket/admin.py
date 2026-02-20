from django.contrib import admin
from .models import Basket, BasketLine, BasketLineAttribute


class BasketLineInline(admin.TabularInline):
    model = BasketLine
    extra = 0


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'customer_id', 'status', 'num_items', 'date_created'
    ]
    list_filter = ['status']
    inlines = [BasketLineInline]


@admin.register(BasketLine)
class BasketLineAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'basket', 'product_id',
        'product_title', 'quantity', 'price_excl_tax'
    ]
