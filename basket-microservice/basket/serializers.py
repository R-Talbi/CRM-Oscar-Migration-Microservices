from rest_framework import serializers
from .models import Basket, BasketLine


class BasketLineSerializer(serializers.ModelSerializer):
    line_price_excl_tax = serializers.ReadOnlyField()
    line_price_incl_tax = serializers.ReadOnlyField()

    class Meta:
        model = BasketLine
        fields = [
            'id', 'product_id', 'product_title',
            'quantity', 'price_excl_tax', 'price_incl_tax',
            'line_price_excl_tax', 'line_price_incl_tax',
            'discount_value', 'stockrecord_id'
        ]


class BasketSerializer(serializers.ModelSerializer):
    lines = BasketLineSerializer(many=True, read_only=True)
    total_excl_tax = serializers.ReadOnlyField()
    total_incl_tax = serializers.ReadOnlyField()
    num_items = serializers.ReadOnlyField()
    num_lines = serializers.ReadOnlyField()
    is_empty = serializers.ReadOnlyField()
    can_be_edited = serializers.ReadOnlyField()

    class Meta:
        model = Basket
        fields = [
            'id', 'customer_id', 'customer_email', 'status',
            'lines', 'total_excl_tax', 'total_incl_tax',
            'num_items', 'num_lines', 'is_empty', 'can_be_edited',
            'voucher_codes', 'date_created', 'date_submitted'
        ]
