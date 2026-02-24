
from rest_framework import serializers
from .models import (
    Order, OrderLine, OrderNote,
    OrderDiscount, OrderStatusChange,
    ShippingAddress, BillingAddress
)


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = '__all__'


class BillingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingAddress
        fields = '__all__'


class OrderLineSerializer(serializers.ModelSerializer):
    discount_incl_tax = serializers.ReadOnlyField()
    discount_excl_tax = serializers.ReadOnlyField()

    class Meta:
        model = OrderLine
        fields = [
            'id', 'partner_name', 'partner_sku',
            'product_id', 'title', 'upc', 'quantity',
            'line_price_incl_tax', 'line_price_excl_tax',
            'line_price_before_discounts_incl_tax',
            'line_price_before_discounts_excl_tax',
            'unit_price_incl_tax', 'unit_price_excl_tax',
            'status', 'discount_incl_tax', 'discount_excl_tax'
        ]


class OrderNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderNote
        fields = '__all__'


class OrderDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDiscount
        fields = '__all__'


class OrderStatusChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusChange
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    date_placed = serializers.DateTimeField(read_only=True)
    lines = OrderLineSerializer(many=True, read_only=True)
    notes = OrderNoteSerializer(many=True, read_only=True)
    discounts = OrderDiscountSerializer(many=True, read_only=True)
    status_changes = OrderStatusChangeSerializer(
        many=True, read_only=True
    )
    total_tax = serializers.ReadOnlyField()
    num_lines = serializers.ReadOnlyField()
    num_items = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = [
            'id', 'number', 'customer_id', 'guest_email',
            'basket_id', 'billing_address', 'shipping_address',
            'currency', 'total_incl_tax', 'total_excl_tax',
            'total_tax', 'shipping_incl_tax', 'shipping_excl_tax',
            'shipping_method', 'status', 'date_placed',
            'num_lines', 'num_items',
            'lines', 'notes', 'discounts', 'status_changes'
        ]
