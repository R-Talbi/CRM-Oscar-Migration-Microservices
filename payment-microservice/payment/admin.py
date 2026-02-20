from django.contrib import admin
from .models import SourceType, Source, Transaction, Bankcard


class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0


@admin.register(SourceType)
class SourceTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code']


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'order_number', 'source_type',
        'amount_allocated', 'amount_debited'
    ]
    inlines = [TransactionInline]


@admin.register(Bankcard)
class BankcardAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_id', 'card_type', 'number']
