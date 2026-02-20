from rest_framework import serializers
from .models import SourceType, Source, Transaction, Bankcard


class SourceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceType
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class SourceSerializer(serializers.ModelSerializer):
    transactions = TransactionSerializer(many=True, read_only=True)
    balance = serializers.ReadOnlyField()
    amount_available_for_refund = serializers.ReadOnlyField()

    class Meta:
        model = Source
        fields = [
            'id', 'order_id', 'order_number',
            'source_type', 'currency',
            'amount_allocated', 'amount_debited',
            'amount_refunded', 'balance',
            'amount_available_for_refund',
            'reference', 'label', 'transactions'
        ]


class BankcardSerializer(serializers.ModelSerializer):
    obfuscated_number = serializers.ReadOnlyField()

    class Meta:
        model = Bankcard
        fields = [
            'id', 'customer_id', 'card_type',
            'name', 'number', 'obfuscated_number',
            'expiry_date', 'partner_reference'
        ]
