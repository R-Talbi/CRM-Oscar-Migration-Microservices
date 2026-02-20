from django.contrib import admin
from .models import Order, OrderLine, OrderNote


class OrderLineInline(admin.TabularInline):
    model = OrderLine
    extra = 0


class OrderNoteInline(admin.TabularInline):
    model = OrderNote
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'number', 'customer_id',
        'status', 'total_incl_tax', 'date_placed'
    ]
    list_filter = ['status']
    inlines = [OrderLineInline, OrderNoteInline]
